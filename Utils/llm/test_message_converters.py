"""Comprehensive tests for message converters."""

from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.message_converter import get_converter, ConverterProvider


class TestOpenAICompletionsConverter:
    """Tests for OpenAI Completions API converter."""

    def test_simple_text_conversation(self):
        """Test basic text conversation without tools."""
        messages = [
            AIMessage.create_user_message("Hello, how are you?"),
            AIMessage.create_assistant_message("I'm doing well, thank you!"),
        ]

        converter = get_converter(ConverterProvider.OPENAI_COMPLETIONS)
        result = converter.convert(messages)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"][0]["type"] == "text"
        assert result[0]["content"][0]["text"] == "Hello, how are you?"

        assert result[1]["role"] == "assistant"
        assert result[1]["content"][0]["type"] == "text"
        assert result[1]["content"][0]["text"] == "I'm doing well, thank you!"

    def test_tool_call_conversation(self):
        """Test conversation with tool calls and responses."""
        messages = [
            AIMessage.create_user_message("List the files please"),
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll list the files for you."),
                    AIMessageContentFactory.create_tool_call("list_files", {}, "call_123"),
                ]
            ),
            AIMessage.create_user_message(
                [AIMessageContentFactory.create_tool_response("list_files", "file1.txt\nfile2.py", "call_123")]
            ),
            AIMessage.create_assistant_message("I found 2 files: file1.txt and file2.py"),
        ]

        converter = get_converter(ConverterProvider.OPENAI_COMPLETIONS)
        result = converter.convert(messages)

        # Should have 4 messages: user, assistant+tool_call, tool_response, assistant
        assert len(result) == 4

        # Check tool call message
        tool_call_msg = result[1]
        assert tool_call_msg["role"] == "assistant"
        assert "tool_calls" in tool_call_msg
        assert len(tool_call_msg["tool_calls"]) == 1
        assert tool_call_msg["tool_calls"][0]["function"]["name"] == "list_files"
        assert tool_call_msg["tool_calls"][0]["id"] == "call_123"

        # Check tool response message
        tool_response_msg = result[2]
        assert tool_response_msg["role"] == "tool"
        assert tool_response_msg["content"] == "file1.txt\nfile2.py"
        assert tool_response_msg["tool_call_id"] == "call_123"

    def test_multimodal_with_image(self):
        """Test conversation with image content."""
        image_data = b"fake_image_data"
        messages = [
            AIMessage.create_user_message(
                [
                    AIMessageContentFactory.create_text("What's in this image?"),
                    AIMessageContentFactory.create_image("test.jpg", image_data),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.OPENAI_COMPLETIONS)
        result = converter.convert(messages)

        assert len(result) == 1
        content = result[0]["content"]
        assert len(content) == 3  # text + filename text + image
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "What's in this image?"
        assert content[1]["type"] == "text"
        assert "test.jpg" in content[1]["text"]
        assert content[2]["type"] == "image_url"
        assert "data:image/jpeg;base64," in content[2]["image_url"]["url"]


class TestOpenAIResponsesConverter:
    """Tests for OpenAI Responses API converter."""

    def test_simple_text_conversation(self):
        """Test basic text conversation."""
        messages = [AIMessage.create_user_message("Hello!"), AIMessage.create_assistant_message("Hi there!")]

        converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
        result = converter.convert(messages)

        assert len(result) == 2

        # First message should be user - check as dict
        user_msg = result[0]
        assert user_msg["role"] == "user"
        assert len(user_msg["content"]) == 1
        assert user_msg["content"][0]["type"] == "input_text"
        assert user_msg["content"][0]["text"] == "Hello!"

        # Second message should be assistant
        assistant_msg = result[1]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"][0]["text"] == "Hi there!"

    def test_tool_calls_separate_items(self):
        """Test that tool calls become separate items in responses format."""
        messages = [
            AIMessage.create_user_message("Run a command"),
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll run that for you."),
                    AIMessageContentFactory.create_tool_call("run_command", {"cmd": "ls"}, "call_456"),
                ]
            ),
            AIMessage.create_user_message(
                [AIMessageContentFactory.create_tool_response("run_command", "file1.txt\nfile2.py", "call_456")]
            ),
        ]

        converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
        result = converter.convert(messages)

        # Should have 4 items: user_msg, assistant_msg, tool_call, tool_response
        assert len(result) == 4

        assistant_msg = result[1]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"][0]["text"] == "I'll run that for you."

        # Check tool call item (as dict) - it comes second in result
        tool_call_item = result[2]
        assert tool_call_item["type"] == "function_call"
        assert tool_call_item["call_id"] == "call_456"
        assert tool_call_item["name"] == "run_command"

        # Check tool response item (as dict) - it comes last
        tool_response_item = result[3]
        assert tool_response_item["type"] == "function_call_output"
        assert tool_response_item["call_id"] == "call_456"
        assert tool_response_item["output"] == "file1.txt\nfile2.py"

    def test_mixed_content_types(self):
        """Test mixed content with text and images."""
        image_data = b"test_image"
        messages = [
            AIMessage.create_user_message(
                [
                    AIMessageContentFactory.create_text("Analyze this:"),
                    AIMessageContentFactory.create_image("chart.png", image_data),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
        result = converter.convert(messages)

        assert len(result) == 1
        content = result[0]["content"]
        assert len(content) == 3  # text + filename + image
        assert content[0]["type"] == "input_text"
        assert content[1]["type"] == "input_text"
        assert "chart.png" in content[1]["text"]
        assert content[2]["type"] == "input_image"

    def test_interleaved_content_order(self):
        """Test that text → tool_call → text maintains correct order."""
        messages = [
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll help you with that."),
                    AIMessageContentFactory.create_tool_call("search", {"query": "test"}, "call_123"),
                    AIMessageContentFactory.create_text("Let me analyze the results."),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
        result = converter.convert(messages)

        # Should have 3 items: text1, tool_call, text2
        assert len(result) == 3

        # First item: text content before tool call
        first_item = result[0]
        assert first_item["role"] == "assistant"
        assert len(first_item["content"]) == 1
        assert first_item["content"][0]["type"] == "input_text"
        assert first_item["content"][0]["text"] == "I'll help you with that."

        # Second item: tool call
        tool_call_item = result[1]
        assert tool_call_item["type"] == "function_call"
        assert tool_call_item["call_id"] == "call_123"
        assert tool_call_item["name"] == "search"

        # Third item: text content after tool call
        third_item = result[2]
        assert third_item["role"] == "assistant"
        assert len(third_item["content"]) == 1
        assert third_item["content"][0]["type"] == "input_text"
        assert third_item["content"][0]["text"] == "Let me analyze the results."


class TestAnthropicConverter:
    """Tests for Anthropic API converter."""

    def test_simple_conversation(self):
        """Test basic conversation format."""
        messages = [
            AIMessage.create_user_message("What's the weather?"),
            AIMessage.create_assistant_message("I'd need your location to check weather."),
        ]

        converter = get_converter(ConverterProvider.ANTHROPIC)
        result = converter.convert(messages)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"][0]["type"] == "text"
        assert result[0]["content"][0]["text"] == "What's the weather?"

        assert result[1]["role"] == "assistant"
        assert result[1]["content"][0]["text"] == "I'd need your location to check weather."

    def test_tool_use_inline(self):
        """Test tool use embedded in message content."""
        messages = [
            AIMessage.create_user_message("Get weather for NYC"),
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll check the weather for you."),
                    AIMessageContentFactory.create_tool_call("get_weather", {"city": "NYC"}, "tool_789"),
                ]
            ),
            AIMessage.create_user_message(
                [AIMessageContentFactory.create_tool_response("get_weather", "Sunny, 75°F", "tool_789")]
            ),
        ]

        converter = get_converter(ConverterProvider.ANTHROPIC)
        result = converter.convert(messages)

        assert len(result) == 3

        # Check assistant message with tool use
        assistant_msg = result[1]
        assert len(assistant_msg["content"]) == 2
        assert assistant_msg["content"][0]["type"] == "text"
        assert assistant_msg["content"][1]["type"] == "tool_use"
        assert assistant_msg["content"][1]["name"] == "get_weather"
        assert assistant_msg["content"][1]["id"] == "tool_789"

        # Check tool result
        tool_result_msg = result[2]
        assert tool_result_msg["content"][0]["type"] == "tool_result"
        assert tool_result_msg["content"][0]["content"] == "Sunny, 75°F"
        assert tool_result_msg["content"][0]["tool_use_id"] == "tool_789"

    def test_image_handling(self):
        """Test image content formatting."""
        image_data = b"anthropic_test_image"
        messages = [
            AIMessage.create_user_message(
                [
                    AIMessageContentFactory.create_text("Describe this image:"),
                    AIMessageContentFactory.create_image("photo.jpg", image_data),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.ANTHROPIC)
        result = converter.convert(messages)

        assert len(result) == 1
        content = result[0]["content"]
        assert len(content) == 3  # text + filename + image
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "text"
        assert "photo.jpg" in content[1]["text"]
        assert content[2]["type"] == "image"
        assert content[2]["source"]["type"] == "base64"
        assert content[2]["source"]["media_type"] == "image/jpeg"


class TestGeminiConverter:
    """Tests for Google Gemini API converter."""

    def test_basic_parts_format(self):
        """Test basic parts-based format."""
        messages = [
            AIMessage.create_user_message("Tell me a joke"),
            AIMessage.create_assistant_message("Why don't scientists trust atoms? Because they make up everything!"),
        ]

        converter = get_converter(ConverterProvider.GEMINI)
        result = converter.convert(messages)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["parts"][0]["text"] == "Tell me a joke"

        assert result[1]["role"] == "assistant"
        assert "atoms" in result[1]["parts"][0]["text"]

    def test_function_calls(self):
        """Test function call parts."""
        messages = [
            AIMessage.create_user_message("Calculate 2+2"),
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll calculate that."),
                    AIMessageContentFactory.create_tool_call("calculator", {"expression": "2+2"}, "calc_001"),
                ]
            ),
            AIMessage.create_user_message(
                [AIMessageContentFactory.create_tool_response("calculator", "4", "calc_001")]
            ),
        ]

        converter = get_converter(ConverterProvider.GEMINI)
        result = converter.convert(messages)

        assert len(result) == 3

        # Check assistant message with function call
        assistant_msg = result[1]
        assert len(assistant_msg["parts"]) == 2
        assert assistant_msg["parts"][0]["text"] == "I'll calculate that."
        # Second part should be the function call Part object
        function_part = assistant_msg["parts"][1]
        assert hasattr(function_part, "function_call")

        # Check function response
        response_msg = result[2]
        response_part = response_msg["parts"][0]
        assert hasattr(response_part, "function_response")

    def test_inline_data_format(self):
        """Test inline data format for images."""
        image_data = b"gemini_image_data"
        messages = [
            AIMessage.create_user_message(
                [
                    AIMessageContentFactory.create_text("What do you see?"),
                    AIMessageContentFactory.create_image("diagram.png", image_data),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.GEMINI)
        result = converter.convert(messages)

        assert len(result) == 1
        parts = result[0]["parts"]
        assert len(parts) == 3  # text + filename + image
        assert parts[0]["text"] == "What do you see?"
        assert "diagram.png" in parts[1]["text"]
        assert "inline_data" in parts[2]
        assert parts[2]["inline_data"]["mime_type"] == "image/png"
        assert parts[2]["inline_data"]["data"] == image_data


class TestAmazonNovaConverter:
    """Tests for Amazon Nova API converter."""

    def test_simple_conversation(self):
        """Test basic conversation format."""
        messages = [
            AIMessage.create_user_message("What's the weather like?"),
            AIMessage.create_assistant_message("I can help you check the weather."),
        ]

        converter = get_converter(ConverterProvider.AMAZON_NOVA)
        result = converter.convert(messages)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"][0]["text"] == "What's the weather like?"

        assert result[1]["role"] == "assistant"
        assert result[1]["content"][0]["text"] == "I can help you check the weather."

    def test_tool_use_format(self):
        """Test tool use and tool response formatting."""
        messages = [
            AIMessage.create_user_message("Check the weather in NYC"),
            AIMessage.create_assistant_message(
                [
                    AIMessageContentFactory.create_text("I'll check the weather for you."),
                    AIMessageContentFactory.create_tool_call("get_weather", {"location": "NYC"}, "tool_123"),
                ]
            ),
            AIMessage.create_user_message(
                [AIMessageContentFactory.create_tool_response("get_weather", "Sunny, 75°F", "tool_123")]
            ),
        ]

        converter = get_converter(ConverterProvider.AMAZON_NOVA)
        result = converter.convert(messages)

        assert len(result) == 3

        # Check assistant message with tool use
        assistant_msg = result[1]
        assert len(assistant_msg["content"]) == 2
        assert assistant_msg["content"][0]["text"] == "I'll check the weather for you."
        assert assistant_msg["content"][1]["toolUse"]["toolUseId"] == "tool_123"
        assert assistant_msg["content"][1]["toolUse"]["name"] == "get_weather"
        assert assistant_msg["content"][1]["toolUse"]["input"] == {"location": "NYC"}

        # Check tool result
        tool_result_msg = result[2]
        assert tool_result_msg["content"][0]["toolResult"]["toolUseId"] == "tool_123"
        assert tool_result_msg["content"][0]["toolResult"]["content"][0]["text"] == "Sunny, 75°F"
        assert tool_result_msg["content"][0]["toolResult"]["status"] == "success"

    def test_image_format(self):
        """Test image content formatting."""
        image_data = b"nova_test_image"
        messages = [
            AIMessage.create_user_message(
                [
                    AIMessageContentFactory.create_text("Analyze this image:"),
                    AIMessageContentFactory.create_image("photo.jpg", image_data),
                ]
            )
        ]

        converter = get_converter(ConverterProvider.AMAZON_NOVA)
        result = converter.convert(messages)

        assert len(result) == 1
        content = result[0]["content"]
        assert len(content) == 3  # text + filename text + image
        assert content[0]["text"] == "Analyze this image:"
        assert "photo.jpg" in content[1]["text"]
        assert content[2]["image"]["format"] == "jpeg"
        assert content[2]["image"]["source"]["bytes"] == image_data


def run_all_tests():
    """Run all tests manually."""

    test_classes = [
        TestOpenAICompletionsConverter,
        TestOpenAIResponsesConverter,
        TestAnthropicConverter,
        TestGeminiConverter,
        TestAmazonNovaConverter,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total_tests += 1
                try:
                    print(f"  {method_name}... ", end="")
                    getattr(instance, method_name)()
                    print("✅ PASSED")
                    passed_tests += 1
                except Exception as e:
                    print(f"❌ FAILED: {e}")
                    failed_tests.append(f"{test_class.__name__}.{method_name}: {e}")

    print(f"\n=== Test Results ===")
    print(f"Total: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")

    if failed_tests:
        print("\nFailed tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
    else:
        print("\n🎉 All tests passed!")

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

from datetime import datetime
from time import sleep
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.shared_params import Reasoning
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputContentParam,
    ResponseInputItemParam,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem,
    ResponseFunctionToolCall,
)

from Utils.llm.ai_message import AIMessage, TextAIMessageContent
from Utils.llm.ai_tool import AIToolSet
from Utils.llm.message_formatter import get_formatter_factory, FormatterProvider
from Utils.llm.config import Model

# Responses API Example
"""
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="o4-mini",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "system message"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Your task is to translate outdated app code to recent version of React using functional components and hooks.\n\nYour task is to:\n1. First use the list_files tool to get the complete file structure of legacy application\n2. Request content of each file and analyze its implementation using the read_file tool\n3. After getting and analyzing all file content - think thoroughly and use the file_structure tool to return the new file structure of translated application\n\nDo not provide any images, application will reuse previous.\nDo not provide any configs.\n\nAfter you return the file structure of the updated application, \nI will request you for each file by the file_path in the list and you should use the write_file tool to give me converted file.\n\n    Apply these instructions for translated application:\n        - Use the following libraries: TypeScript.\n        - Split the code into separate components.\n        - Optimize the code where possible.\n        - The converted code should not contain any TODOs.\n    \n\nDo not add any comments in generated code and follow the instructions precisely. Once you finish the whole task, please use the end_task tool.\n"
        }
      ]
    },
    {
      "type": "reasoning",
      "id": "rs_6862793d91088198bbcb437f5796c7e405561eb377a63632",
      "summary": [
        {
          "type": "summary_text",
          "text": "**Planning app code update**\n\nThe user wants to rewrite outdated app code to use the latest React version with functional components and hooks while introducing TypeScript. They plan to start by using a function to list the existing file structure, then analyze each file and propose a new structure. Importantly, I shouldn't provide any unrequested content yet, so I’ll focus on making that initial call to list the files so the user can move to the next step."
        },
        {
          "type": "summary_text",
          "text": "**Preparing to list files**\n\nI need to start by calling a function to get the current file structure, so my next message will focus on that. I'll make the call to list the files, and then I have to wait for the result. It’s an important first step, so I’m getting everything ready for this function call in the commentary. Once I have the file structure, I can move on to the next steps with the user."
        }
      ]
    },
    {
      "type": "function_call",
      "id": "fc_68627942c3048198a68102f6f4efa50505561eb377a63632",
      "call_id": "call_TB1Zs7jI0LddcgpGM1FBuNd1",
      "name": "list_files",
      "arguments": "{}"
    },
    {
      "type": "function_call_output",
      "call_id": "call_TB1Zs7jI0LddcgpGM1FBuNd1",
      "output": "{\n  \"status\": \"success\",\n  \"data\": [\n    \"file1.txt\",\n    \"file2.txt\",\n    \"image1.png\",\n    \"document.pdf\",\n    \"notes.docx\"\n  ],\n  \"message\": \"File list retrieved successfully.\"\n}"
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "is it ok or not?"
        }
      ]
    },
    {
      "type": "reasoning",
      "id": "rs_686279d2fe008198b2cc77dd535403dc05561eb377a63632",
      "summary": [
        {
          "type": "summary_text",
          "text": "**Clarifying the user's request**\n\nThe user is asking if the file list is okay, which might mean they want to confirm its correctness. I think it’s best to seek clarification. I could say something like, \"I've listed these files. Are these the ones for the legacy app? If so, we can proceed with reading the content.\" I also need to consider that the list includes irrelevant files, so I should verify they're looking for code files before continuing."
        },
        {
          "type": "summary_text",
          "text": "**Seeking confirmation on file list**\n\nI need to clarify with the user about the file list since it includes non-code files. I could ask, “Are these the actual files you need? Do you have any code?” I should provide a concise message stating the files listed, like file1.txt, file2.txt, and image1.png, and confirm if these represent the legacy app code. I’ll ask if I should proceed to read their content or if there's an issue that needs addressing."
        }
      ]
    },
    {
      "id": "msg_686279d87cf081988b9609b6a7fcc26905561eb377a63632",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "I’ve retrieved the following file list:\n\n• file1.txt  \n• file2.txt  \n• image1.png  \n• document.pdf  \n• notes.docx  \n\nDo these represent your legacy app’s codebase? If so, shall I proceed to request and analyze each file’s contents?"
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "text"
    }
  },
  reasoning={
    "effort": "medium",
    "summary": "auto"
  },
  tools=[
    {
      "type": "function",
      "name": "list_files",
      "description": "Lists all files in the current directory",
      "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
        "required": []
      },
      "strict": True
    }
  ],
  store=True
)
"""


def request_openai_responses_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: AIToolSet = None
) -> Dict[str, Any]:
    """
    Request data from OpenAI Responses API.

    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration

    Returns:
        Dictionary containing response content, thoughts, and token usage

    Raises:
        Exception: If API request fails or configuration is invalid
    """
    config = model()
    developer_message: List[ResponseInputItemParam] = [EasyInputMessageParam(role="developer", content=system_prompt)]
    formatter_factory = get_formatter_factory(FormatterProvider.OPENAI_RESPONSES)

    input_messages: List[ResponseInputItemParam] = []
    for message in messages:
        api_message_content: List[ResponseInputContentParam] = []
        for content in message.content:
            try:
                formatted_content = formatter_factory.format_content(content)
                api_message_content.extend(formatted_content)
            except ValueError as e:
                print(f"OpenAI responses API: {e}")

        # ToDo: incorrect, this code add only messages with roles and content, but responses API need different formats, look above example
        input_messages.append(
            EasyInputMessageParam(role="user" if message.role == "user" else "assistant", content=api_message_content)
        )

    try:
        client = OpenAI()
        resp = client.responses.create(
            tools=tools.to_openai_responses_format() if tools else None,
            model=config["model_id"],
            input=developer_message + input_messages,
            max_output_tokens=config["max_tokens"],
            temperature=config["temperature"],
            reasoning=Reasoning(effort=config["reasoning_effort"]),
            background=True,
        )
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client or create response: {e}")

    print(f"Response ID: {resp.id}")

    try:
        while resp.status in {"queued", "in_progress"}:
            print(f"\r\tResponse status: {resp.status} | Last update: {datetime.now()}", end="", flush=True)
            sleep(30)
            resp = client.responses.retrieve(resp.id)
        print()
    except Exception as e:
        raise Exception(f"Failed to retrieve response: {e}")

    response = resp.output

    content = next(
        (
            item.content[0].text
            for item in response
            if isinstance(item, ResponseOutputMessage)
            and isinstance(item.content[0], ResponseOutputText)
            and len(item.content) > 0
        ),
        None,
    )
    reasoning = "\n".join(
        summary.text
        for item in response
        if isinstance(item, ResponseReasoningItem)
        for summary in item.summary
        if summary.text
    )

    tool_calls = [
        {
            "name": item.name,
            "arguments": item.arguments,
            "id": item.call_id,
        }
        for item in response
        if isinstance(item, ResponseFunctionToolCall)
    ]

    result = {
        "content": content,
        "thoughts": reasoning,
        "tool_calls": tool_calls,
        "tokens": {
            "input_tokens": resp.usage.input_tokens if resp.usage else None,
            "output_tokens": resp.usage.output_tokens if resp.usage else None,
            "reasoning_tokens": (resp.usage.output_tokens_details.reasoning_tokens if resp.usage else None),
        },
    }

    return result


if __name__ == "__main__":
    data = request_openai_responses_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage(role="user", content=[TextAIMessageContent(text="Send me a recipe for banana bread.")])],
        model=Model.OpenAi_o3_0416,
    )

    print("Thoughts:", data["thoughts"], sep="\n")
    print("Content:", data["content"], sep="\n")
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")

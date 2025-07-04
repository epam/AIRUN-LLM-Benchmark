import json
import time
from pathlib import Path
import os
from typing import List

from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.api import ask_model
from Utils.llm.config import ModelProvider, Model
from Utils.llm.ai_tool import AITool, AIToolParameter, AIToolSet
from Utils.llm.tool_handler import ToolHandlerFactory

RESULTS_BASE_PATH = os.getenv("RESULTS_REPO_PATH")

# Create tools using the new AITool class
tool_set = AIToolSet()

# Add list_files tool
list_files_tool = AITool(name="list_files", description="List all files in the legacy directory")
tool_set.add_tool(list_files_tool)

# Add read_file tool
read_file_tool = AITool(
    name="read_file",
    description="Read the content of a file from the legacy application",
    parameters=[AIToolParameter("file_path", "string", "Path to the file to read", required=True)],
)
tool_set.add_tool(read_file_tool)

# Add file_structure tool
file_structure_tool = AITool(
    name="file_structure",
    description="Return the new file structure of the new application",
    parameters=[
        AIToolParameter(
            "file_paths", "array", "List of file paths for the new application", required=True, items_type="string"
        )
    ],
)
tool_set.add_tool(file_structure_tool)

# Add write_file tool
write_file_tool = AITool(
    name="write_file",
    description="Write converted code to a file in the new application",
    parameters=[
        AIToolParameter("file_path", "string", "Path where the file should be written", required=True),
        AIToolParameter("content", "string", "The converted code content", required=True),
    ],
)
tool_set.add_tool(write_file_tool)

# Add end_task tool
end_task_tool = AITool(name="end_task", description="End the translation task when complete")
tool_set.add_tool(end_task_tool)

SYSTEM_PROMPT = """
As an AI proficient in software engineering, particularly in Frontend development, React and Angular, 
your objective is to resolve the provided development tasks.

Use the provided tools to interact with the legacy application files and create the new React application.
Use the tools in the following order:
1. Use list_files to get the complete file structure of the legacy application
2. Use read_file to read and analyze each legacy file
3. Use file_structure to return the new React application structure  
4. Use write_file for each file when requested
5. Use end_task when the translation is complete
"""

TASK = """
{objective}

Your task is to:
1. First use the list_files tool to get the complete file structure of legacy application
2. Request content of each file and analyze its implementation using the read_file tool
3. After getting and analyzing all files content - think thoroughly and use the file_structure tool to return the new file structure of translated application

Do not provide any images, application will reuse previous.
Do not provide any configs.

After you return the file structure of the updated application, 
You need to provide the converted code for each file in the new application structure using write_file tool to give me converted file.
{instructions}

Do not add any comments in generated code and follow the instructions precisely. Once you finish the whole task, please use the end_task tool.
"""


def run_experiment(task, model, dataset_path, output_path, start_time):
    messages: List[AIMessage] = []
    input_tokens = output_tokens = reasoning_tokens = 0
    requests_list = [AIMessage.create_user_message(task)]

    task_in_progress = True
    while task_in_progress:
        if len(requests_list) > 0:
            messages.append(requests_list.pop())
            print(f"Requests left: {len(requests_list)}")
        else:
            break

        if len(messages) > 0:
            print("REQUEST:")
            print(messages[-1])

        answer = ask_model(messages, SYSTEM_PROMPT, model, tools=tool_set)
        print("RESPONSE:")
        print(json.dumps(answer, indent=4))

        tokens = answer["tokens"]
        input_tokens += tokens["input_tokens"]
        output_tokens += tokens["output_tokens"]
        reasoning_tokens += tokens.get("reasoning_tokens", 0)

        content = answer["content"]
        thoughts = answer["thoughts"]

        # Use factory method to create assistant message
        use_model_role = model.provider == ModelProvider.AISTUDIO
        assistant_message = AIMessage.create_assistant_message(content or [], use_model_role)
        messages.append(assistant_message)

        tools_content = []
        # Handle tool calls using the strategy pattern
        if "tool_calls" in answer and answer["tool_calls"]:
            for tool_call in answer["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]
                tool_id = tool_call["id"]

                # Add tool call to the message
                tool_call_content = AIMessageContentFactory.create_tool_call(tool_name, tool_args, tool_id)
                messages[-1].content.append(tool_call_content)

                # Handle end_task specially
                if tool_name == "end_task":
                    print("Ending task.")
                    task_in_progress = False
                    break

                # Use the tool handler factory to get appropriate handler
                try:
                    handler = ToolHandlerFactory.create_handler(tool_name, dataset_path, output_path)
                    response_messages = handler.handle(tool_name, tool_args, tool_id)
                    tools_content.append(response_messages)
                except ValueError as e:
                    # Handle unknown tools
                    error_message = f"Unknown tool: {tool_name}. Please use only supported tools: read_file, write_file, file_structure, list_files, end_task"
                    error_response = AIMessageContentFactory.create_text(error_message)
                    tools_content.append(error_response)
        else:
            # Handle case where no tool calls are made
            prompt_message = "Please use the provided tools to complete the task."
            prompt_response = AIMessageContentFactory.create_text(prompt_message)
            tools_content.append(prompt_response)

        requests_list.append(AIMessage.create_user_message(tools_content))

    end_time = int(time.time())
    output = {
        "messages": [message.__dict__ for message in messages],
        "time": end_time - start_time,
        "total_tokens": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
        },
    }
    messages_log = json.dumps(output, indent=4, default=str)
    messages_log_path = Path(output_path, "message_log.json")
    with open(messages_log_path, "w") as file:
        file.write(messages_log)


# ----------------------- do not remove comment -----------------------
if __name__ == "__main__":
    # model = Model.Codex_Mini_Latest
    # model = Model.Gemini_25_Flash_0520
    # model = Model.Sonnet_4
    # model = Model.Grok3mini_beta
    # model = Model.DeepSeekV3_0324
    model = Model.GPT41_0414
    current_unix_time = int(time.time())
    base_path = Path(__file__).resolve().parent.parent
    DATASET_PATH = base_path / "Dataset/JS/Piano_NativeJS"
    OUTPUT_PATH = Path(f"{RESULTS_BASE_PATH}/Output/{model}/JS/contextual_experiment/native/{current_unix_time}/")

    OBJECTIVE = (
        "Your task is to translate outdated app code to recent version of React using functional components and hooks."
    )

    INSTRUCTIONS = f"""
    Apply these instructions for translated application:
        - Use the following libraries: TypeScript.
        - Split the code into separate components.
        - Optimize the code where possible.
        - The converted code should not contain any TODOs.
    """

    task = TASK.format(objective=OBJECTIVE, instructions=INSTRUCTIONS)

    print(task)

    run_experiment(
        task=task, model=model, dataset_path=DATASET_PATH, output_path=OUTPUT_PATH, start_time=current_unix_time
    )

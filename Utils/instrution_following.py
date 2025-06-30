import json
import time
from pathlib import Path
import os

from Utils.llm.ai_message import AIMessage, TextAIMessageContent, ToolCallAIMessageContent, ToolResponseAIMessageContent
from Utils.llm.api import ask_model
from Utils.llm.config import ModelProvider, Model
from Utils.llm.ai_tool import AITool, AIToolParameter, AIToolSet

RESULTS_BASE_PATH = os.getenv('RESULTS_REPO_PATH')

# Create tools using the new AITool class
tool_set = AIToolSet()

# Add list_files tool
list_files_tool = AITool(
    name="list_files",
    description="List all files in the legacy directory"
)
tool_set.add_tool(list_files_tool)

# Add read_file tool
read_file_tool = AITool(
    name="read_file",
    description="Read the content of a file from the legacy application",
    parameters=[AIToolParameter("file_path", "string", "Path to the file to read", required=True)]
)
tool_set.add_tool(read_file_tool)

# Add file_structure tool
file_structure_tool = AITool(
    name="file_structure",
    description="Return the new file structure of the new application",
    parameters=[
        AIToolParameter("file_paths", "array", "List of file paths for the new application", required=True, items_type="string")
    ]
)
tool_set.add_tool(file_structure_tool)

# Add write_file tool
write_file_tool = AITool(
    name="write_file",
    description="Write converted code to a file in the new application",
    parameters=[
        AIToolParameter("file_path", "string", "Path where the file should be written", required=True),
        AIToolParameter("content", "string", "The converted code content", required=True)
    ]
)
tool_set.add_tool(write_file_tool)

# Add end_task tool
end_task_tool = AITool(
    name="end_task",
    description="End the translation task when complete"
)
tool_set.add_tool(end_task_tool)

# Convert to the format needed by your current model provider
# TOOLS = tool_set.to_anthropic_format()  # or tool_set.to_openai_format() for OpenAI

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
3. After getting and analyzing all file content - think thoroughly and use the file_structure tool to return the new file structure of translated application

Do not provide any images, application will reuse previous.
Do not provide any configs.

After you return the file structure of the updated application, 
I will request you for each file by the file_path in the list and you should use the write_file tool to give me converted file.
{instructions}

Do not add any comments in generated code and follow the instructions precisely. Once you finish the whole task, please use the end_task tool.
"""


def list_files(base_path):
    base_path = Path(base_path)
    file_list = []
    for file_path in base_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(base_path)
            file_list.append(str(relative_path))

    return file_list


def run_experiment(task, model, dataset_path, output_path, start_time):
    messages: list[AIMessage] = []
    input_tokens = output_tokens = reasoning_tokens = 0
    requests_list = [AIMessage(role="user", content=[TextAIMessageContent(text=task)])]
    files_read_by_model = 0

    while True:
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

        tokens = answer["tokens"]  # {'input_tokens': 168, 'output_tokens': 2031, 'reasoning_tokens': 576}
        input_tokens += tokens['input_tokens']
        output_tokens += tokens['output_tokens']
        reasoning_tokens += tokens.get('reasoning_tokens', 0)
        ai_role = "model" if model.provider == ModelProvider.AISTUDIO else "assistant"

        content = answer["content"]

        messages.append(AIMessage(role=ai_role, content=[TextAIMessageContent(text=content)] if content else []))

        # Handle tool calls instead of JSON commands
        if "tool_calls" in answer and answer["tool_calls"]:
            tool_call = answer["tool_calls"][0]  # Handle first tool call
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            tool_id = tool_call["id"]

            messages[-1].content.append(ToolCallAIMessageContent(tool_name, tool_args, tool_id))

            if tool_name == "end_task":
                print("Ending task.")
                break
            elif tool_name == "list_files":
                try:
                    file_list = list_files(dataset_path)
                    files_content = "\n".join(file_list)
                    response = [ToolResponseAIMessageContent(tool_name, files_content, tool_id)]
                    requests_list.append(AIMessage(role="user", content=response))
                except Exception as e:
                    print(f"Error listing files at {dataset_path}: {e}")
                    content = f"Error: Could not list files directory files"
                    response = [TextAIMessageContent(text=content)]
                    requests_list.append(AIMessage(role="user", content=response))
            elif tool_name == "read_file":
                file_path = tool_args["file_path"]
                full_path = Path(dataset_path, file_path)
                response = []
                try:
                    with open(full_path, 'r') as file:
                        content = file.read()
                        response = [ToolResponseAIMessageContent(tool_name, content, tool_id)]
                        files_read_by_model += 1
                except FileNotFoundError:
                    print(f"Error: File at {full_path} not found.")
                    content = f"Error: File at {file_path} not found or file_path is incorrect."
                    response = [TextAIMessageContent(text=content)]

                requests_list.append(AIMessage(role="user", content=response))
            elif tool_name == "write_file":
                response = []
                file_path = tool_args["file_path"]
                full_path = Path(output_path, file_path.lstrip('/'))
                full_path.parent.mkdir(parents=True, exist_ok=True)
                content = tool_args["content"]
                try:
                    with open(full_path, 'w') as file:
                        if ".json" in file_path:
                            json.dump(content, file, indent=4)
                        else:
                            file.write(content)
                    print(f"File written successfully at {file_path}.")
                    response = [ToolResponseAIMessageContent(tool_name, "File written successfully", tool_id)]
                except IOError as e:
                    print(f"Failed to write file at {file_path}. Error: {e}")
                    response = [ToolResponseAIMessageContent(tool_name, "Failed to write file", tool_id)]
                messages.append(AIMessage(role="user", content=response))
            elif tool_name == "file_structure":
                file_paths = tool_args["file_paths"]
                for path in file_paths:
                    requests_list.append(AIMessage(role="user", content=[TextAIMessageContent(text=f"Give me converted code of {path}")]))
                    print(path)
                messages.append(AIMessage(role="user", content=[ToolResponseAIMessageContent(tool_name, "File structure received successfully", tool_id)]))
            else:
                reply = f"Unknown tool: {tool_name}. Please use only supported tools: read_file, write_file, file_structure, list_files, end_task"
                requests_list.append(AIMessage(role="user", content=[TextAIMessageContent(text=reply)]))
            # Todo - add log to results directory and read from it
        else:
            # Handle case where no tool calls are made
            reply = "Please use the provided tools to complete the task."
            requests_list.append(AIMessage(role="user", content=[TextAIMessageContent(text=reply)]))

    end_time = int(time.time())
    output = {
        # ToDo: check here Mikhail, is it ok to call __dict__ on AIMessage?
        "messages": [message.__dict__ for message in messages],
        "time": end_time - start_time,
        "total_tokens": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
        }
    }
    messages_log = json.dumps(output, indent=4, default=str)
    messages_log_path = Path(output_path, "message_log.json")
    with open(messages_log_path, 'w') as file:
        file.write(messages_log)

# ----------------------- do not remove comment -----------------------
if __name__ == "__main__":
    model = Model.Codex_Mini_Latest
    current_unix_time = int(time.time())
    base_path = Path(__file__).resolve().parent.parent
    DATASET_PATH = base_path / "Dataset/JS/Piano_NativeJS"
    # OUTPUT_PATH = f"{RESULTS_BASE_PATH}/Output/{model}/JS/contextual_experiment/translate_to_react/{current_unix_time}/"
    OUTPUT_PATH = f"{RESULTS_BASE_PATH}/Output/{model}/JS/contextual_experiment/native/{current_unix_time}/"

    # OBJECTIVE = "Your task is to translate outdated AngularJS app code to recent version of React using functional components and hooks."
    OBJECTIVE = "Your task is to translate outdated app code to recent version of React using functional components and hooks."

    # INSTRUCTIONS = f"""
    # Apply these instructions for translated application:
    #     - Use the following libraries: TypeScript, Redux Toolkit with createSlice, and nanoid.
    #     - Provide configuration of the store and provider if needed.
    #     - Split the code into separate components.
    #     - Optimize the code where possible.
    #     - The converted code should not contain any TODOs.
    #     - Return the translated code as markdown code snippets.
    #     - Simply return the codebase without additional comments or explanations on how to convert it.
    # """

    INSTRUCTIONS = f"""
    Apply these instructions for translated application:
        - Use the following libraries: TypeScript.
        - Split the code into separate components.
        - Optimize the code where possible.
        - The converted code should not contain any TODOs.
    """


    task = TASK.format(
        objective=OBJECTIVE,
        instructions=INSTRUCTIONS
    )

    print(task)

    run_experiment(
        task=task,
        model=model,
        dataset_path=DATASET_PATH,
        output_path=OUTPUT_PATH,
        start_time=current_unix_time
    )


# output = {
#     "messages": [AIMessage(role="user", content=[TextAIMessageContent(text=task)])],
# }
# messages_log = json.dumps(output,default=lambda x: x.__dict__, indent=4)
#
# with open("message_log.json", 'w') as file:
#     file.write(messages_log)
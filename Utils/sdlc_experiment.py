import json
import time
from pathlib import Path
import os
from typing import List, Dict, Any

from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.api import ask_model
from Utils.llm.config import ModelProvider, Model
from Utils.llm.ai_tool import AITool, AIToolParameter, AIToolSet

RESULTS_BASE_PATH = os.getenv("RESULTS_REPO_PATH")

tool_set = AIToolSet()

submit_solution_tool = AITool(
    name="submit_solution",
    description="Submit current code",
    parameters=[
        AIToolParameter("content", "string", "The current code", required=True),
        AIToolParameter("changes_description", "string", "Description of what was changed/added", required=True),
    ],
)
tool_set.add_tool(submit_solution_tool)

SYSTEM_PROMPT = """
You are an experienced software frontend engineer.
Your goal is to write code based on requirements and guidance.

Use the submit_solution tool to:
1. Submit your current code
2. Describe what changes you made
"""


class SDLCExperimentHandler:
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.step_count = 0

    def handle_submit_solution(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str) -> AIMessage:
        self.step_count += 1

        content = tool_args["content"]
        changes_description = tool_args["changes_description"]

        step_path = self.output_path / f"step_{self.step_count}"
        step_path.mkdir(parents=True, exist_ok=True)

        code_file_path = step_path / "component.tsx"
        with open(code_file_path, "w") as f:
            f.write(content)

        changes_file_path = step_path / "changes.txt"
        with open(changes_file_path, "w") as f:
            f.write(f"Step {self.step_count} Changes:\n{changes_description}")

        response_text = f"Step {self.step_count} saved. Changes: {changes_description}\n\nWaiting for next guidance..."

        return AIMessage.create_user_message(
            [AIMessageContentFactory.create_tool_response(tool_name, response_text, tool_id)]
        )


def run_sdlc_experiment(
    task: str,
    model: Model,
    output_path: str,
    start_time: int,
    max_steps: int = 10,
    steps: List[str] = None,
):
    messages: List[AIMessage] = []
    input_tokens = output_tokens = reasoning_tokens = 0
    requests_list = [AIMessage.create_user_message(task)]

    handler = SDLCExperimentHandler(output_path)
    task_in_progress = True
    current_step = 0
    step_index = 0

    while task_in_progress and current_step < max_steps:
        if len(requests_list) > 0:
            messages.append(requests_list.pop())
        else:
            break

        if len(messages) > 0:
            print(f"STEP {current_step + 1} REQUEST:")
            print(messages[-1])

        answer = ask_model(messages, SYSTEM_PROMPT, model, tools=tool_set)
        print("RESPONSE:")
        print(json.dumps(answer, indent=4))

        tokens = answer["tokens"]
        input_tokens += tokens["input_tokens"]
        output_tokens += tokens["output_tokens"]
        reasoning_tokens += tokens.get("reasoning_tokens", 0)

        content = answer["content"]

        use_model_role = model.provider == ModelProvider.AISTUDIO
        assistant_message = AIMessage.create_assistant_message(content or [], use_model_role)
        messages.append(assistant_message)

        if "tool_calls" in answer and answer["tool_calls"]:
            for tool_call in answer["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]
                tool_id = tool_call["id"]

                tool_call_content = AIMessageContentFactory.create_tool_call(tool_name, tool_args, tool_id)
                messages[-1].content.append(tool_call_content)

                if tool_name == "submit_solution":
                    response_msg = handler.handle_submit_solution(tool_name, tool_args, tool_id)

                    if steps and step_index < len(steps):
                        next_step_text = steps[step_index]
                        step_index += 1
                        response_msg.content.append(AIMessageContentFactory.create_text(next_step_text))
                        requests_list.append(response_msg)
                    else:
                        task_in_progress = False
        else:
            prompt_message = "Please use the provided tools to complete the SDLC task."
            prompt_response = AIMessageContentFactory.create_text(prompt_message)
            requests_list.append(AIMessage.create_user_message([prompt_response]))

        current_step += 1

    end_time = int(time.time())
    output = {
        "messages": [message.__dict__ for message in messages],
        "time": end_time - start_time,
        "steps": current_step,
        "total_tokens": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
        },
    }

    messages_log = json.dumps(output, indent=4, default=str)
    messages_log_path = Path(output_path, "sdlc_log.json")
    with open(messages_log_path, "w") as file:
        file.write(messages_log)

    print(f"SDLC experiment completed after {current_step} steps.")
    print(f"Messages log saved to {messages_log_path}")


def main(
    model: Model,
    initial_task: str,
    experiment_name: str = "sdlc_experiment",
    steps: List[str] = None,
    max_steps: int = 10,
):

    current_unix_time = int(time.time())
    output_path = Path(f"{RESULTS_BASE_PATH}/Output/{model}/SDLC/{experiment_name}/{current_unix_time}/")
    output_path.mkdir(parents=True, exist_ok=True)

    print("Starting SDLC Experiment:")
    print(initial_task)

    run_sdlc_experiment(
        task=initial_task,
        model=model,
        output_path=str(output_path),
        start_time=current_unix_time,
        max_steps=max_steps,
        steps=steps,
    )


if __name__ == "__main__":
    # API DataTable Experiment
    API_DATATABLE_TASK = """
    Create a React component that fetches user data from an API and displays it in a data table

    Requirements:
    1. Create a React component called DataTableComponent
    2. Component should fetch data from '/api/users' endpoint
    3. Display the fetched user data in a table format with data-testid="table"
    4. Show user fields: id, name, email, role, status
    5. Handle loading states and errors gracefully
    6. Export the component as a default export
    7. Use TypeScript for type safety
    8. Add data-testid attributes for testing: table, loading elements

    Instructions:
    Component should be exported as a default export.
    Use functional components with hooks.
    Focus on clean data fetching and table display.
    Ensure the table is properly structured with headers.
    Add data-testid attributes to key elements for testing purposes.

    Create the initial implementation and submit it using submit_solution tool.
    """

    API_DATATABLE_STEPS = [
        "Add a loading spinner using the 'react-spinners' library. Import and use a spinner component (like ClipLoader or PulseLoader) to show while data is being fetched. Add data-testid='loader' to the loading element.",
        "Add search and filter functionality. Include a search input field (data-testid='search-input') to filter users by name, and dropdown filters for role (data-testid='role-filter') and status (data-testid='status-filter'). Add a clear filters button with data-testid='clear-filters'.",
    ]

    main(
        model=Model.GPT41_0414,
        initial_task=API_DATATABLE_TASK,
        experiment_name="api_datatable_experiment",
        steps=API_DATATABLE_STEPS,
        max_steps=3,
    )

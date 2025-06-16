import os
from pathlib import Path
from datetime import datetime
from Utils.llm.api import ask_model
from Utils.llm.config import Model
from Utils.llm.ai_message import (
    AIMessage,
    AIMessageContent,
    TextAIMessageContent,
    ImageAIMessageContent,
)


def get_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    except UnicodeDecodeError:
        print(f"Can't read file {file_path} it's not a text")
        return None


def name_without_extension(file_name: str) -> str:
    parts = file_name.split(".", 1)
    return parts[0]


def get_output_folder_name(answers_path, current_datetime, report_name):
    formatted_datetime = str(current_datetime).replace(" ", "_").replace(":", "-")
    return os.path.join(answers_path, "result_" + formatted_datetime, report_name)


def generate_report(
    answers_path, file_content, data, report_name, attempt, current_datetime
):
    current_output_path = get_output_folder_name(
        answers_path, current_datetime, name_without_extension(report_name)
    )
    if not os.path.exists(current_output_path):
        os.makedirs(current_output_path)
    output_file_path = (
        os.path.join(str(current_output_path), name_without_extension(report_name))
        + f"_report_{attempt}.md"
    )
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(file_content + "\n" + data)


def get_answer_from_model(
    content_list: list[AIMessageContent], system_prompt: str, model, attempt: int = 1
):
    data = ask_model(
        messages=[AIMessage(role="user", content_list=content_list)],
        system_prompt=system_prompt,
        model=model,
        attempt=attempt,
    )

    if "error" in data:
        return data["error"]

    thoughts = f'### Thoughts:\n{data["thoughts"]}\n\n' if data["thoughts"] else ""
    print(f"\tSuccess! Execution time: {data['execute_time']}")

    return (
        f"{thoughts}"
        f'### Answer:\n{data["content"]}\n\n'
        f'### Tokens: {str(data["tokens"])}\n'
        f'### Execution time: {data["execute_time"]}\n'
    )


def get_questions_by_path(directory_path):
    files = []
    if not os.path.exists(directory_path):
        return files

    items = os.listdir(directory_path)

    for item in items:
        file_path = os.path.join(directory_path, item)
        if os.path.isfile(file_path) and item != "system.txt":
            files.append(item)
    return files


def generate_answers_from_files(
    category: Path,
    output_dir,
    model,
    current_datetime,
    attempts_count,
    launch_list,
    skip_list,
):
    system_prompt = get_file_content(category / "system.txt")
    if system_prompt is None:
        print(
            f"System prompt not found in {category}, continue without system prompt..."
        )
        system_prompt = ""
    questions = get_questions_by_path(category)

    for question_name in questions:
        if launch_list and question_name not in launch_list:
            continue
        if skip_list and question_name in skip_list:
            continue

        for attempt in range(1, attempts_count + 1):
            file_content = get_file_content(category / question_name)
            if file_content is None:
                print(f"File {question_name} is empty or not readable, skipping...")
                break
            message_content: list[AIMessageContent] = []
            message_content.append(TextAIMessageContent(text=file_content))

            print(f"Attempt #{attempt}, get answer for {question_name}")
            data = f"## Run {attempt}:\n"
            data += get_answer_from_model(message_content, system_prompt, model)
            generate_report(
                output_dir, file_content, data, question_name, attempt, current_datetime
            )


def main(model: Model, lang, attempts_count, launch_list, skip_list):
    print(f"Starting answers generation for {model}")
    current_datetime = datetime.now()
    base_path = Path(__file__).resolve().parent.parent
    results_path = Path(os.getenv("RESULTS_REPO_PATH")).resolve()

    categories_path = base_path / "Scenarios" / "Tasks_Enriched" / lang

    for category in categories_path.iterdir():
        if not category.is_dir():
            continue

        output_dir = results_path / "Output" / f"{model}" / lang / category.name

        generate_answers_from_files(
            category,
            output_dir,
            model,
            current_datetime,
            attempts_count,
            launch_list,
            skip_list,
        )


if __name__ == "__main__":
    main(Model.Sonnet_37, "JS", 1, ["GenerateReactApp.md"], [])

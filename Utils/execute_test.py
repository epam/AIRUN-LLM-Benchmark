import os
from pathlib import Path
from datetime import datetime
from Utils.enrich_tasks import enrich_task_content
from Utils.llm.api import ask_model
from Utils.llm.config import Model
from Utils.llm.ai_message import AIMessage, AIMessageContent, TextAIMessageContent, ImageAIMessageContent


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


def generate_report(answers_path, file_content, data, report_name, attempt, current_datetime):
    current_output_path = get_output_folder_name(answers_path, current_datetime, name_without_extension(report_name))
    if not os.path.exists(current_output_path):
        os.makedirs(current_output_path)
    output_file_path = (
        os.path.join(str(current_output_path), name_without_extension(report_name)) + f"_report_{attempt}.md"
    )
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(file_content + "\n" + data)


def get_answer_from_model(content_list: list[AIMessageContent], system_prompt: str, model, attempt: int = 1):
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


def get_tasks_by_path(directory_path):
    files = []
    if not os.path.exists(directory_path):
        return files

    items = os.listdir(directory_path)

    for item in items:
        file_path = os.path.join(directory_path, item)
        if os.path.isfile(file_path) and item != "system.txt":
            files.append(item)
    return files


def get_task_images(images_category: Path) -> list[ImageAIMessageContent]:
    images = []
    if not images_category.exists() or not images_category.is_dir():
        return images

    for image_file in images_category.iterdir():
        if image_file.is_file():
            with open(image_file, "rb") as img_file:
                images.append(ImageAIMessageContent(binary_content=img_file.read(), file_name=image_file.name))
    return images


def generate_answers_from_files(
    task_category: Path,
    datasets_category: Path,
    output_dir,
    model,
    current_datetime,
    attempts_count,
    launch_list,
    skip_list,
):
    system_prompt = get_file_content(task_category / "system.txt")
    if system_prompt is None:
        print(f"System prompt not found in {task_category}, continue without system prompt...")
        system_prompt = ""
    tasks = get_tasks_by_path(task_category)

    for task_name in tasks:
        if launch_list and task_name not in launch_list:
            continue
        if skip_list and task_name in skip_list:
            continue

        for attempt in range(1, attempts_count + 1):
            task_content = get_file_content(task_category / task_name)
            if task_content is None:
                print(f"Skipping task {task_name} due to read error.")
                break

            task_content = enrich_task_content(task_name, task_content, datasets_category)
            message_content: list[AIMessageContent] = [TextAIMessageContent(text=task_content)]
            images_category = task_category / task_name.replace(".md", "_images")
            message_content.extend(get_task_images(images_category))

            print(f"Attempt #{attempt}, get answer for {task_name}")
            data = f"## Run {attempt}:\n"
            data += get_answer_from_model(message_content, system_prompt, model)
            generate_report(output_dir, task_content, data, task_name, attempt, current_datetime)


def main(model: Model, lang, attempts_count, launch_list, skip_list):
    print(f"Starting answers generation for {model}")
    current_datetime = datetime.now()
    base_path = Path(__file__).resolve().parent.parent
    results_path = Path(str(os.getenv("RESULTS_REPO_PATH"))).resolve()

    tasks_category = base_path / "Scenarios" / "Tasks" / lang
    datasets_category = base_path / "Dataset" / lang

    for task_category in tasks_category.iterdir():
        if not task_category.is_dir():
            continue

        output_dir = results_path / "Output" / f"{model}" / lang / task_category.name

        generate_answers_from_files(
            task_category,
            datasets_category,
            output_dir,
            model,
            current_datetime,
            attempts_count,
            launch_list,
            skip_list,
        )


if __name__ == "__main__":
    main(Model.GPT4o_1120, "JS", 1, ["GenerateReactApp.md"], [])

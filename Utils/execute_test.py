import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from Utils.enrich_tasks import enrich_task_content
from Utils.llm.api import ask_model
from Utils.llm.config import Model
from Utils.llm.ai_message import AIMessage, AIMessageContent, TextAIMessageContent, ImageAIMessageContent
from typing import Optional


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


def report_exists(output_dir: Path, report_name: str, attempt: int) -> bool:
    """Check if a report already exists for the given task and attempt."""
    # Check all result_* folders in the output directory
    if not output_dir.exists():
        return False

    for result_folder in output_dir.glob("result_*"):
        if not result_folder.is_dir():
            continue

        task_folder = result_folder / name_without_extension(report_name)
        if not task_folder.exists():
            continue

        report_file = task_folder / f"{name_without_extension(report_name)}_report_{attempt}.md"
        if report_file.exists():
            return True

    return False


def generate_report(
    answers_path: Path,
    content: list[AIMessageContent],
    data: str,
    report_name: str,
    attempt: int,
    current_datetime: datetime,
):
    current_output_path = get_output_folder_name(answers_path, current_datetime, name_without_extension(report_name))
    if not os.path.exists(current_output_path):
        os.makedirs(current_output_path)
    output_file_path = (
        os.path.join(str(current_output_path), name_without_extension(report_name)) + f"_report_{attempt}.md"
    )
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join([str_content.__str__() for str_content in content]) + "\n\n" + data)


def get_answer_from_model(task_name: str, content: list[AIMessageContent], system_prompt: str, model, attempt: int = 1):
    print(f"[{task_name}] Starting attempt #{attempt}")
    data = ask_model(
        messages=[AIMessage(role="user", content=content)],
        system_prompt=system_prompt,
        model=model,
        attempt=attempt,
    )

    if "error" in data:
        return data["error"]

    thoughts = f'### Thoughts:\n{data["thoughts"]}\n\n' if data["thoughts"] else ""
    print(f"[{task_name}] Completed attempt #{attempt} in {data['execute_time']} seconds")

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


def get_model_answer_task(
    message_content: list[AIMessageContent],
    system_prompt: str,
    model: Model,
    task_name: str,
    attempt: int,
):
    data = f"## Run {attempt}:\n"
    data += get_answer_from_model(task_name, message_content, system_prompt, model, attempt)
    return task_name, attempt, message_content, data


def generate_answers_from_files(
    task_category: Path,
    datasets_category: Path,
    output_dir: Path,
    model: Model,
    current_datetime: datetime,
    attempts_count: int,
    launch_list: list[str],
    skip_list: list[str],
    skip_existing: bool = True,
):
    system_prompt = get_file_content(task_category / "system.txt")
    if system_prompt is None:
        print(f"System prompt not found in {task_category}, continue without system prompt...")
        system_prompt = ""
    tasks = get_tasks_by_path(task_category)

    # Prepare all tasks and their message content
    task_jobs = []
    for task_name in tasks:
        if launch_list and task_name not in launch_list:
            continue
        if skip_list and task_name in skip_list:
            continue

        for attempt in range(1, attempts_count + 1):
            # Check if report already exists
            if skip_existing and report_exists(output_dir, task_name, attempt):
                print(f"[{task_name}] Report for attempt #{attempt} already exists, skipping...")
                continue

            task_content = get_file_content(task_category / task_name)
            if task_content is None:
                print(f"Skipping task {task_name} due to read error.")
                break

            task_content = enrich_task_content(task_name, task_content, datasets_category)
            message_content: list[AIMessageContent] = [TextAIMessageContent(text=task_content)]
            images_category = task_category / task_name.replace(".md", "_images")
            message_content.extend(get_task_images(images_category))

            task_jobs.append((message_content, task_name, attempt))

    if len(task_jobs) > 0:
        # Execute all get_answer_from_model calls in parallel
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for message_content, task_name, attempt in task_jobs:
                future = executor.submit(
                    get_model_answer_task,
                    message_content,
                    system_prompt,
                    model,
                    task_name,
                    attempt,
                )
                futures.append(future)

            # Collect results and generate reports
            for future in concurrent.futures.as_completed(futures):
                task_name, attempt, message_content, data = future.result()
                generate_report(output_dir, message_content, data, task_name, attempt, current_datetime)


def main(
    model: Model,
    lang: str,
    attempts_count: int,
    launch_list: Optional[list[str]] = None,
    skip_list: Optional[list[str]] = None,
    categories_launch_list: Optional[list[str]] = None,
    categories_skip_list: Optional[list[str]] = None,
    skip_existing: bool = True,
):
    print(f"Starting answers generation for {model}")
    current_datetime = datetime.now()
    base_path = Path(__file__).resolve().parent.parent
    results_path = Path(str(os.getenv("RESULTS_REPO_PATH"))).resolve()

    tasks_category = base_path / "Scenarios" / "Tasks" / lang
    datasets_category = base_path / "Dataset" / lang

    for task_category in tasks_category.iterdir():
        if not task_category.is_dir():
            continue
        if categories_launch_list and task_category.name not in categories_launch_list:
            continue
        if categories_skip_list and task_category.name in categories_skip_list:
            continue

        output_dir: Path = results_path / "Output" / f"{model}" / lang / task_category.name

        generate_answers_from_files(
            task_category,
            datasets_category,
            output_dir,
            model,
            current_datetime,
            attempts_count,
            launch_list,
            skip_list,
            skip_existing,
        )


if __name__ == "__main__":
    main(Model.GPT52_1211_high, "JS", 1, launch_list=[], categories_skip_list=['multimodal'], skip_existing=True)

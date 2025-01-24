import os
from pathlib import Path
from datetime import datetime
from Utils.llm.api import ask_model


def get_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except UnicodeDecodeError:
        print(f'Can\'t read file {file_path} it\'s not a text')
        return None


def name_without_extension(file_name: str) -> str:
    parts = file_name.split('.', 1)
    return parts[0]


def get_output_folder_name(answers_path, current_datetime, report_name):
    formatted_datetime = str(current_datetime).replace(' ', '_').replace(':', '-')
    return os.path.join(answers_path, 'result_' + formatted_datetime, report_name)


def generate_report(answers_path, file_content, data, report_name, attempt, current_datetime):
    current_output_path = get_output_folder_name(answers_path, current_datetime, name_without_extension(report_name))
    if not os.path.exists(current_output_path):
        os.makedirs(current_output_path)
    output_file_path = os.path.join(current_output_path, name_without_extension(report_name)) + f'_report_{attempt}.md'
    with open(output_file_path, 'w', encoding="utf-8") as output_file:
        output_file.write(file_content + '\n' + data)
    print(f"Output was written to {output_file_path}")


def get_answer_from_model(prompt, system_prompt, model, attempt=1):
    data = ask_model(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=system_prompt,
        model=model,
        attempt=attempt
    )

    if "error" in data:
        return data["error"]

    thoughts = f'### Thoughts:\n{data["thoughts"]}\n\n' if data["thoughts"] else ''

    return (f'{thoughts}'
            f'### Answer:\n{data["content"]}\n\n'
            f'### Tokens: {str(data["tokens"])}\n'
            f'### Execution time: {data["execute_time"]}\n')


def get_questions_by_path(directory_path):
    files = []
    if not os.path.exists(directory_path):
        return files

    items = os.listdir(directory_path)

    for item in items:
        file_path = os.path.join(directory_path, item)
        if os.path.isfile(file_path):
            files.append(item)
    return files


def generate_answers_from_files(paths, model, current_datetime, attempts_count, launch_list, skip_list):
    system_prompt = get_file_content(paths["system_prompt_path"])
    questions = get_questions_by_path(paths["task_path"])

    for question_name in questions:
        if launch_list and question_name not in launch_list: continue
        if skip_list and question_name in skip_list: continue

        for attempt in range(attempts_count):
            file_content = get_file_content(os.path.join(paths["task_path"], question_name))
            print(f'Attempt #{attempt + 1}, get answer for {question_name}')
            data = '## Run ' + str(attempt + 1) + ':\n'
            data += get_answer_from_model(file_content, system_prompt, model)
            generate_report(paths["output_path"], file_content, data, question_name, attempt + 1, current_datetime)


def main(model, lang, attempts_count, launch_list, skip_list):
    print(f"Starting answers generation for {model}")
    current_datetime = datetime.now()
    base_path = Path(__file__).resolve().parent.parent
    results_path = Path(os.getenv('RESULTS_REPO_PATH')).resolve()

    categories_path = base_path / "Scenarios" / "Compiled_Tasks" / model / lang

    for category in categories_path.iterdir():
        if not category.is_dir(): continue

        paths = {
            "system_prompt_path": base_path / "Scenarios" / "Task_Templates" / model / lang / category.name / "system.txt",
            "task_path": base_path / "Scenarios" / "Compiled_Tasks" / model / lang / category.name,
            "output_path": results_path / "Output" / model / lang / category.name
        }
        generate_answers_from_files(paths, model, current_datetime, attempts_count, launch_list, skip_list)

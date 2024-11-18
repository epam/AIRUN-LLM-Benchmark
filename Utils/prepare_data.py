import os
import json
from pathlib import Path
from Utils.constants import repo_to_complexity

base_path = Path(__file__).resolve().parent.parent


def traverse_files_and_generate_questions(root_folder: str):
    output = []
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(file_path, root_folder)
            extension = file.split('.')[-1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output.append(f'{relative_path}\n'
                              f'```{extension}\n{content}\n```\n')
                print(f'Appending {relative_path}')
            except UnicodeDecodeError:
                print(f'Can\'t read file {file_path}, it\'s not a text file')
    return "\n".join(output)


def use_template_and_write(template_file_path: str, output_file_path: str, replacement_string: str):
    with open(template_file_path, 'r') as input_file:
        content = input_file.read()

    modified_content = content.replace('<place code here>', replacement_string)

    with open(output_file_path, 'w', encoding="utf-8") as output_file:
        output_file.write(modified_content)


def modify_output_filename(output_filename: str, repo_name: str):
    complexity = repo_to_complexity.get(repo_name)
    name, extension = output_filename.rsplit('.', 1)
    return f'{name}_{repo_name}_{complexity}.{extension}'


def generate_questions(templates_path, template, output_path, repo_path=None, repo_name=None):
    content_to_insert = traverse_files_and_generate_questions(repo_path) if repo_path else ''

    template_path = os.path.join(templates_path, template)

    os.makedirs(output_path, exist_ok=True)
    output_filename = modify_output_filename(template, repo_name) if repo_name else template
    output_file_path = os.path.join(output_path, output_filename)
    use_template_and_write(template_path, output_file_path, content_to_insert)
    print(f"Output was written to {output_file_path}")


def main(model, lang):
    print(f"Starting question generation for {model}")

    config_path = base_path / "Config" / model / f"{lang}.json"
    print(config_path)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for goal_type, repos_mapper in config.items():
        templates_path = base_path / "Scenarios" / "Task_Templates" / model / lang / goal_type
        output_path = base_path / "Scenarios" / "Compiled_Tasks" / model / lang / goal_type

        for template, repos in repos_mapper.items():
            if not repos:  # no repos to insert
                generate_questions(templates_path, template, output_path)
                continue
            for repo_name in repos:  # repos is array
                repo_path = base_path / "Dataset" / lang / repo_name
                print(repo_name)
                generate_questions(templates_path, template, output_path, repo_path, repo_name)

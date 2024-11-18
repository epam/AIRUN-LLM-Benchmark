import os
import re
from pathlib import Path
from dotenv import load_dotenv

from Utils.constants import repo_to_technology

load_dotenv()
results_path = Path(os.getenv('RESULTS_REPO_PATH')).resolve()


def extract_and_write_data(file_path, model, experiment):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()

        file_name = Path(file_path).stem
        category, attempt = file_name.split('_report_')

        tokens_regex = r"### Tokens: {'input_tokens': (\d+), 'output_tokens': (\d+)(?:, 'reasoning_tokens': (\d+))?}"
        execution_time_regex = r"### Execution time: ([\d.]+)"

        tokens_match = re.search(tokens_regex, data)
        execution_time_match = re.search(execution_time_regex, data)

        category_name, _, repo_and_complexity = category.partition('_')

        repo_name = ci = size = 'none'
        if repo_and_complexity:
            regex = r"^(.+?)_((?:low|avg|high|extra_high))_((?:low|avg|high|extra_high)(?:_\d)?)"
            match = re.match(regex, repo_and_complexity)
            if match:
                repo_name, ci, size = match.groups()

        if tokens_match and execution_time_match:
            input_tokens, output_tokens, reasoning_tokens = tokens_match.groups()
            reasoning_tokens = reasoning_tokens or '0'
            execution_time = execution_time_match.group(1)
        else:
            print(f"No available data {file_name}.")
            input_tokens = output_tokens = execution_time = reasoning_tokens = '0'

        csv_line = f"{experiment},{category_name},{repo_to_technology.get(repo_name, 'none')},{model},{repo_name},{ci},{size},{attempt},{input_tokens},{reasoning_tokens},{output_tokens},{execution_time}\n"
        return csv_line
    except Exception as e:
        print(f'Error while processing file: {e}')


def process_directory(directory_path, model, experiment):
    data = ''
    for category_folder in os.listdir(directory_path):
        entry_path = os.path.join(directory_path, category_folder)
        try:
            for file in sorted(os.scandir(entry_path), key=lambda x: x.name):
                if re.match(r'.*report_\d+\.md$', file.name):
                    data += extract_and_write_data(file.path, model, experiment)
        except Exception as e:
            print(f'Error while reading directory: {e}')
    return data


default_experiments = [
    'code_analysis',
    'code_explanation',
    'component_generation',
    'solution_documentation',
    'solution_migration',
    'solution_template_generation',
    'test_generation'

    # 'code_documentation',
    # 'code_generation',
    # 'code_translation'
]


def main(models=None, langs=None, experiments=default_experiments):
    header = "Experiment,Category,Language,Models,Dataset,Complexity,Size,Attempt,Input,Reasons,Output,Time,Accuracy,Completeness\n"
    for model in models:
        for lang in langs:
            data = header
            for experiment in experiments:
                current_path = results_path / 'Output' / model / lang / experiment
                if not os.path.isdir(current_path): continue
                for experiment_folder in os.listdir(current_path):
                    if experiment_folder.startswith('.'): continue
                    experiment_folder_path = current_path / experiment_folder
                    data += process_directory(experiment_folder_path, model, experiment)

            output_path = results_path / 'Output' / model / lang / 'summary.csv'
            with open(output_path, 'w') as f:
                f.write(data)
            print(f'Summary written successfully for {model} and lang {lang} to {output_path}')


if __name__ == "__main__":
    main(['ChatGPT4o_august_0509'], ['JS'])

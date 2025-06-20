import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from Utils.constants import repo_to_technology
from Utils.llm.config import Model

load_dotenv()
results_path = Path(os.getenv("RESULTS_REPO_PATH")).resolve()

type_mapper = {
    "code_analysis": "code_documentation",
    "code_explanation": "code_documentation",
    "solution_documentation": "code_documentation",
    "component_generation": "code_generation",
    "solution_template_generation": "code_generation",
    "test_generation": "code_generation",
    "solution_migration": "code_translation",
    "bug_fixing": "bug_fixing",
}


def extract_and_write_data(file_path, model, experiment):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()

        file_name = Path(file_path).stem
        category, attempt = file_name.split("_report_")

        tokens_regex = r"### Tokens: {'input_tokens': (\d+), 'output_tokens': (\d+)(?:, 'reasoning_tokens': (\d+))?}"
        execution_time_regex = r"### Execution time: ([\d.]+)"

        tokens_match = re.search(tokens_regex, data)
        execution_time_match = re.search(execution_time_regex, data)

        category_name, _, repo_and_complexity = category.partition("_")

        repo_name = ci = size = "none"
        if repo_and_complexity:
            regex = r"^(.+?)_((?:low|avg|high|extra_high))_((?:low|avg|high|extra_high)(?:_\d)?)"
            match = re.match(regex, repo_and_complexity)
            if match:
                repo_name, ci, size = match.groups()

        if tokens_match and execution_time_match:
            input_tokens, output_tokens, reasoning_tokens = tokens_match.groups()
            reasoning_tokens = reasoning_tokens or "0"
            execution_time = round(float(execution_time_match.group(1)), 2)
        else:
            print(f"No available data {file_name}.")
            input_tokens = output_tokens = execution_time = reasoning_tokens = "0"

        csv_line = f"{type_mapper[experiment]},{experiment},{category_name},{repo_to_technology.get(repo_name, 'none')},{model},{repo_name},{ci},{size},{attempt},{input_tokens},{reasoning_tokens},{output_tokens},{execution_time}\n"
        return csv_line
    except Exception as e:
        print(f"Error while processing file: {e}")


def process_directory(directory_path, model, experiment):
    data = ""
    for category_folder in os.listdir(directory_path):
        entry_path = os.path.join(directory_path, category_folder)
        try:
            for file in sorted(os.scandir(entry_path), key=lambda x: x.name):
                if re.match(r".*report_\d+\.md$", file.name):
                    data += extract_and_write_data(file.path, model, experiment)
        except Exception as e:
            print(f"Error while reading directory: {e}")
    return data


default_types = [
    "solution_migration",  # code_translation
    "component_generation",  # code_generation
    "test_generation",  # code_generation
    "solution_template_generation",  # code_generation
    "code_analysis",  # code_documentation
    "code_explanation",  # code_documentation
    "solution_documentation",  # code_documentation
    "bug_fixing",  # bug_fixing
    # 'code_documentation',
    # 'code_generation',
    # 'code_translation'
]


def main(models: List[Model] = None, langs=None, experiments=None):
    if experiments is None:
        experiments = default_types
    header = "Experiment,Type,Category,Language,Models,Dataset,Complexity,Size,Attempt,Input,Reasons,Output,Time,Accuracy,Completeness\n"
    for model in models:
        for lang in langs:
            data = header
            target_dir = results_path / "Output" / model.model_id / lang
            for experiment in experiments:
                current_path = target_dir / experiment
                if not os.path.isdir(current_path):
                    continue
                for experiment_folder in os.listdir(current_path):
                    if experiment_folder.startswith("."):
                        continue
                    experiment_folder_path = current_path / experiment_folder
                    data += process_directory(experiment_folder_path, model, experiment)

            output_path = target_dir / "summary.csv"
            with open(output_path, "w") as f:
                f.write(data)
            print(f"Summary written successfully for {model} and lang {lang} to {output_path}")


if __name__ == "__main__":
    main([Model.Sonnet_37], ["JS"])

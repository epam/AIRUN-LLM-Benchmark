import os
import re
import threading
import pandas as pd
import concurrent.futures
from pathlib import Path
from typing import Callable, List, Tuple, Any
from dotenv import load_dotenv
from datetime import datetime

from epam.auto_llm_eval.evaluator import (
    read_file,
    write_file,
    evaluate_output,
    grade_report,
    Criteria,
    CriteriaEvalStep,
)
from Utils.llm.ai_message import AIMessage, TextAIMessageContent
from Utils.llm.config import Model
from Utils.llm.api import ask_model

load_dotenv()

results_repo_path = os.getenv("RESULTS_REPO_PATH")
if not results_repo_path:
    raise ValueError("RESULTS_REPO_PATH environment variable is not set. Please set it before running the script.")

gcloud_project_id = os.getenv("GCLOUD_PROJECT_ID")
if not gcloud_project_id:
    raise ValueError("GCLOUD_PROJECT_ID environment variable is not set. Please set it before running the script.")

results_path = Path(results_repo_path).resolve()
criteria_path = Path(results_repo_path) / "Criteria" / "JS"


class EvaluationModel:
    execute_prompt: Callable[[str], str]
    name: str

    def __init__(self, name: str, execute_prompt: Callable[[str], str]):
        self.name = name
        self.execute_prompt = execute_prompt


def get_evaluation_models() -> List[EvaluationModel]:
    def extract_json_from_md(content: str) -> str:
        json_text = content
        json_text = json_text.strip("\n")
        json_text = json_text.strip("`")
        json_text = json_text.replace("json\n", "", 1)

        return json_text

    # GPT-5
    def execute_gpt5(prompt: str) -> str:
        response = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.GPT5_0807,
            verbose=False,
        )

        if response.get("error", None):
            raise ValueError(f"Error from GPT-5: {response['error']}")

        return extract_json_from_md(response["content"])

    gpt5 = EvaluationModel(name="GPT-5", execute_prompt=execute_gpt5)

    # Sonnet 4
    def execute_sonnet4(prompt: str) -> str:
        response = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Sonnet_4_Thinking,
            verbose=False,
        )

        if response.get("error", None):
            raise ValueError(f"Error from Sonnet-4: {response['error']}")

        return extract_json_from_md(response["content"])

    sonnet = EvaluationModel(name="Sonnet-4", execute_prompt=execute_sonnet4)

    # Gemini 2.5 Pro
    def execute_gemini(prompt: str) -> str:
        response = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Gemini_25_Pro_0605,
            verbose=False,
        )

        if response.get("error", None):
            raise ValueError(f"Error from Gemini-2.5-Pro: {response['error']}")

        return extract_json_from_md(response["content"])

    gemini = EvaluationModel(name="Gemini-2.5-Pro", execute_prompt=execute_gemini)

    return [gpt5, sonnet, gemini]


def construct_category_name(category, dataset, complexity, size):
    """Construct the category name."""
    # Example: AngularToReact, AngularJSCosmoPage, avg, high => AngularToReact_AngularJSCosmoPage_avg_high
    parts = [category]
    if dataset:
        parts.append(dataset)
    if complexity:
        parts.append(complexity)
    if size:
        parts.append(size)
    return "_".join(parts)


def extract_content(file_path) -> str:
    """Extract the content from the file."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regular expression to find content between "### Answer:\n" and "\n### Tokens:"
    pattern = re.compile(r"### Answer:\n(.*?)\n### Tokens:", re.DOTALL)
    match = pattern.search(content)

    if match:
        return match.group(1).strip()
    else:
        return ""


def get_completeness_filename(scenario_name: str, model_name: str) -> str:
    return f"{scenario_name}_{model_name}_completeness.json"


def get_accuracy_filename(scenario_name: str, model_name: str) -> str:
    return f"{scenario_name}_{model_name}_accuracy.json"


def evaluate(model: Model, language: str = "JS", force_reevaluate: bool = False, summary_filename: str = "summary.csv"):
    """
    Main function to evaluate the scenarios.

    This function evaluates the scenarios for a given model and language.
    It loads the evaluation models, reads the summary file,
    and evaluates the scenarios based on the criteria.

    Args:
        model (Model): Model to evaluate.
        language (str): The programming language of scenarios.

    Returns:
        None
    """

    evaluation_models = get_evaluation_models()
    base_path = results_path / "Output" / model.model_id / language
    summary_path = base_path / summary_filename

    if not summary_path.exists():
        print_error(f"ERROR: File {summary_path} does not exist.")
        return

    summary_report = pd.read_csv(summary_path)
    for index, row in summary_report.iterrows():
        experiment_type = row["Type"]
        category = row["Category"]
        dataset = row["Dataset"] if row["Dataset"] != "none" else ""
        complexity = row["Complexity"] if row["Complexity"] != "none" else ""
        size = row["Size"] if row["Size"] != "none" else ""
        category_name = construct_category_name(category, dataset, complexity, size)

        for root, dirs, files in os.walk(base_path / experiment_type):
            if category_name in dirs:
                print()
                category_path = Path(root) / category_name
                category_criteria_path = criteria_path / experiment_type / f"{category_name}_criteria.yaml"

                if not category_criteria_path.exists():
                    print_error(f"ERROR: File {category_criteria_path} does not exist.")
                    continue

                try:
                    criteria_yaml = read_file(category_criteria_path)
                    criteria = Criteria.from_yaml(criteria_yaml)
                except Exception as e:
                    print_error(f"ERROR: Unable to read or parse criteria from {category_criteria_path}: {e}")
                    continue

                output = extract_content(category_path / f"{category_name}_report_1.md")
                if not output:
                    print_error(f"ERROR: Scenario {category_name} has no output. Skipping evaluation.")
                    continue

                print_regular(f"Evaluating scenario {category_name} at {datetime.now()}...")
                print_lock = threading.Lock()

                def process_evaluation_model(
                    evaluation_model: EvaluationModel, report_path: Path, eval_steps: List[CriteriaEvalStep]
                ):
                    if report_path.exists() and not force_reevaluate:
                        with print_lock:
                            print_skip(f"Skipping {report_path.name} as it already exists.")
                        return

                    try:
                        report_json = evaluate_output(
                            evaluation_steps=eval_steps, output=output, execute_prompt=evaluation_model.execute_prompt
                        )
                        write_file(report_path, report_json)
                        with print_lock:
                            if force_reevaluate:
                                print_success(f"File updated: {report_path.name}")
                            else:
                                print_success(f"File created: {report_path.name}")
                    except Exception as e:
                        with print_lock:
                            print_error(f"ERROR: unable to create or update {report_path.name}: {e}")

                threads = []
                # Accuracy evaluation threads
                for evaluation_model in evaluation_models:
                    thread = threading.Thread(
                        target=process_evaluation_model,
                        args=(
                            evaluation_model,
                            category_path / get_accuracy_filename(category_name, evaluation_model.name),
                            criteria.evaluation_steps.accuracy,
                        ),
                    )
                    threads.append(thread)
                    thread.start()

                # Completeness evaluation threads
                for evaluation_model in evaluation_models:
                    thread = threading.Thread(
                        target=process_evaluation_model,
                        args=(
                            evaluation_model,
                            category_path / get_completeness_filename(category_name, evaluation_model.name),
                            criteria.evaluation_steps.completeness,
                        ),
                    )
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()


def grade(model: Model, language: str = "JS", force_regrade: bool = False, summary_filename: str = "summary.csv"):
    """
    Main function to grade the scenarios.

    This function grades the scenarios for a given model and language.
    It loads the evaluation models, reads the summary file,
    and grades the scenarios based on the evaluation reports.

    Args:
        model (Model): Model to evaluate.
        language (str): The programming language of scenarios.

    Returns:
        None
    """

    evaluation_models = get_evaluation_models()
    base_path = results_path / "Output" / model.model_id / language
    summary_path = base_path / summary_filename

    if not summary_path.exists():
        print_error(f"ERROR: File {summary_path} does not exist.")
        return

    summary_report = pd.read_csv(summary_path)
    for index, row in summary_report.iterrows():
        experiment_type = row["Type"]
        category = row["Category"]
        dataset = row["Dataset"] if row["Dataset"] != "none" else ""
        complexity = row["Complexity"] if row["Complexity"] != "none" else ""
        size = row["Size"] if row["Size"] != "none" else ""
        category_name = construct_category_name(category, dataset, complexity, size)

        acc, comp = row.get("Accuracy", None), row.get("Completeness", None)

        if pd.notna(acc) and pd.notna(comp) and not force_regrade:
            print_skip(f"Skipping {category_name} as it already has results.")
            continue

        for root, dirs, files in os.walk(base_path / experiment_type):
            if category_name in dirs:
                category_path = Path(root) / category_name
                errors = 0

                for evaluation_model in evaluation_models:
                    accuracy_cell_model_name = f"Accuracy_{evaluation_model.name}"
                    acc_value = row.get(accuracy_cell_model_name, None)
                    if pd.notna(acc_value) and not force_regrade:
                        print_skip(
                            f"Skipping accuracy grading for {category_name} by {evaluation_model.name} as it already has results."
                        )
                    else:
                        accuracy_report_path = category_path / get_accuracy_filename(
                            category_name, evaluation_model.name
                        )
                        if not accuracy_report_path.exists():
                            print_error(
                                f"ERROR: Accuracy report not found for {category_name} by {evaluation_model.name}."
                            )
                            errors += 1
                        else:
                            try:
                                accuracy_report = read_file(accuracy_report_path)
                                accuracy_grading = grade_report(accuracy_report)
                                summary_report.at[index, accuracy_cell_model_name] = round(
                                    accuracy_grading.get_score(), 2
                                )
                            except Exception as e:
                                print_error(
                                    f"ERROR: Failed to process accuracy report for {category_name} by {evaluation_model.name}: {e}"
                                )
                                errors += 1

                    completeness_cell_model_name = f"Completeness_{evaluation_model.name}"
                    comp_value = row.get(completeness_cell_model_name, None)
                    if pd.notna(comp_value) and not force_regrade:
                        print_skip(
                            f"Skipping completeness grading for {category_name} by {evaluation_model.name} as it already has results."
                        )
                    else:
                        completeness_report_path = category_path / get_completeness_filename(
                            category_name, evaluation_model.name
                        )
                        if not completeness_report_path.exists():
                            print_error(
                                f"ERROR: Completeness report not found for {category_name} by {evaluation_model.name}."
                            )
                            errors += 1
                        else:
                            try:
                                completeness_report = read_file(completeness_report_path)
                                completeness_grading = grade_report(completeness_report)
                                summary_report.at[index, completeness_cell_model_name] = round(
                                    completeness_grading.get_score(), 2
                                )
                            except Exception as e:
                                print_error(
                                    f"ERROR: Failed to process completeness report for {category_name} by {evaluation_model.name}: {e}"
                                )
                                errors += 1

                if errors == 0:
                    # calculate average accuracy and completeness by models evaluations
                    summary_report.at[index, "Accuracy"] = round(
                        summary_report.loc[index, [f"Accuracy_{model.name}" for model in evaluation_models]].mean(), 2
                    )

                    summary_report.at[index, "Completeness"] = round(
                        summary_report.loc[index, [f"Completeness_{model.name}" for model in evaluation_models]].mean(),
                        2,
                    )
                    print_success(f"Average accuracy and completeness calculated for {category_name}.")

                summary_report.to_csv(summary_path, index=False)


def print_colored(text, color):
    # ANSI escape codes for colors
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "dark_gray": "\033[90m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")


def print_error(text):
    print_colored(text, "red")


def print_success(text):
    print_colored(text, "green")


def print_skip(text):
    print_colored(text, "dark_gray")


def print_regular(text):
    print_colored(text, "white")


if __name__ == "__main__":
    evaluate(Model.Gemini_25_Pro_0605, "JS")

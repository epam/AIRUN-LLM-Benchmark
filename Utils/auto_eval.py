import os
import re
import threading
import pandas as pd
from pathlib import Path
from typing import Callable, List
from dotenv import load_dotenv
from datetime import datetime

from epam.auto_llm_eval.evaluator import (
    evaluate_output,
    read_file,
    write_file,
    Criteria,
    CriterionEvalStep,
    EvaluationResult,
    GradeResult,
)
from Utils.llm.ai_message import AIMessage, TextAIMessageContent
from Utils.llm.config import Model
from Utils.llm.api import ask_model
from Utils.llm.response_model import LLMResponse

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

    # GPT-5.2
    def execute_gpt(prompt: str) -> str:
        response: LLMResponse = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.GPT52_1211_high,
            verbose=False,
        )

        if response.error:
            raise ValueError(f"Error from GPT-5.2: {response.error}")

        return extract_json_from_md(response.content)

    gpt = EvaluationModel(name="GPT-5.2", execute_prompt=execute_gpt)

    # Sonnet 4.5
    def execute_sonnet(prompt: str) -> str:
        response: LLMResponse = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Sonnet_45,
            verbose=False,
        )

        if response.error:
            raise ValueError(f"Error from Sonnet-4.5: {response.error}")

        return extract_json_from_md(response.content)

    sonnet = EvaluationModel(name="Sonnet-4.5", execute_prompt=execute_sonnet)

    # Gemini 3.0 Pro
    def execute_gemini(prompt: str) -> str:
        response: LLMResponse = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Gemini_3_Pro_Preview,
            verbose=False,
        )

        if response.error:
            raise ValueError(f"Error from Gemini-3-Pro: {response.error}")

        return extract_json_from_md(response.content)

    gemini = EvaluationModel(name="Gemini-3-Pro", execute_prompt=execute_gemini)

    return [gpt, sonnet, gemini]


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


def get_eval_bucket_filename(scenario_name: str, model_name: str, eval_bucket_name: str) -> str:
    return f"{scenario_name}_{model_name}_{eval_bucket_name}.json"


def evaluate(model: Model, language: str = "JS", force_reevaluate: bool = False, summary_filename: str = "summary.csv") -> tuple[str, ...]:
    """
    Main function to evaluate the scenarios.

    This function evaluates the scenarios for a given model and language.
    It loads the evaluation models, reads the summary file,
    and evaluates the scenarios based on the criteria.

    Args:
        model (Model): Model to evaluate.
        language (str): The programming language of scenarios.

    Returns:
        tuple[str, ...] - criterion types
    """

    evaluation_models = get_evaluation_models()
    base_path = results_path / "Output" / model.model_id / language
    summary_path = base_path / summary_filename

    if not summary_path.exists():
        print_error(f"ERROR: File {summary_path} does not exist.")
        return ()

    criterion_types = set()
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
                    evaluation_model: EvaluationModel, report_path: Path, eval_steps: tuple[CriterionEvalStep, ...]
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

                for evaluation_model in evaluation_models:
                    for evaluation_steps_bucket in criteria.evaluation_steps_buckets():
                        criterion_types.add(evaluation_steps_bucket.name)
                        thread = threading.Thread(
                            target=process_evaluation_model,
                            args=(
                                evaluation_model,
                                category_path / get_eval_bucket_filename(category_name, evaluation_model.name, evaluation_steps_bucket.name),
                                evaluation_steps_bucket.evaluation_steps,
                            ),
                        )
                        threads.append(thread)
                        thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()

    return tuple(criterion_types)


def grade(model: Model, language: str = "JS", force_regrade: bool = False, summary_filename: str = "summary.csv", criterion_types: tuple[str, ...] = ("Accuracy", "Completeness")):
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
    # add columns for criterion type average values if they don't exist
    for criterion_type in criterion_types:
        if criterion_type not in summary_report.columns:
            summary_report[criterion_type] = None

    for index, row in summary_report.iterrows():
        experiment_type = row["Type"]
        category = row["Category"]
        dataset = row["Dataset"] if row["Dataset"] != "none" else ""
        complexity = row["Complexity"] if row["Complexity"] != "none" else ""
        size = row["Size"] if row["Size"] != "none" else ""
        category_name = construct_category_name(category, dataset, complexity, size)

        if all(pd.notna(row.get(type_, None)) for type_ in criterion_types) and not force_regrade:
            print_skip(f"Skipping {category_name} as it already has results.")
            continue

        for root, dirs, files in os.walk(base_path / experiment_type):
            if category_name in dirs:
                category_path = Path(root) / category_name
                errors = 0

                for evaluation_model in evaluation_models:
                    for criterion_type in criterion_types:
                        cell_model_name = f"{criterion_type}_{evaluation_model.name}"
                        value = row.get(cell_model_name, None)
                        if pd.notna(value) and not force_regrade:
                            print_skip(
                                f"Skipping {criterion_type} grading for {category_name} by {evaluation_model.name} as it already has results."
                            )
                        else:
                            report_path = category_path / get_eval_bucket_filename(
                                category_name, evaluation_model.name, criterion_type
                            )
                            if not report_path.exists():
                                print_error(
                                    f"ERROR: {criterion_type} report not found for {category_name} by {evaluation_model.name}."
                                )
                                errors += 1
                            else:
                                try:
                                    report = read_file(report_path)
                                    eval_result = EvaluationResult(criterion_type, report)
                                    grading = GradeResult.from_evaluation_result(eval_result)
                                    summary_report.at[index, cell_model_name] = round(grading.get_score(), 2)
                                except Exception as e:
                                    print_error(
                                        f"ERROR: Failed to process {criterion_type} report for {category_name} by {evaluation_model.name}: {e}"
                                    )
                                    errors += 1

                if errors == 0:
                    # calculate average values by models evaluations
                    for criterion_type in criterion_types:
                        summary_report.at[index, criterion_type] = round(
                            summary_report.loc[index, [f"{criterion_type}_{model.name}" for model in evaluation_models]].mean(), 2
                        )
                    print_success(f"Average {criterion_type} values calculated for {category_name}.")

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
    evaluate(Model.Sonnet_46, "JS")

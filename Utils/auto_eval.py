import os
import re
import pandas as pd
import concurrent.futures
from pathlib import Path
from typing import Callable, List, Tuple, Any
from dotenv import load_dotenv

from epam.auto_llm_eval.evaluator import (
    read_file,
    write_file,
    evaluate_scenario,
    grade_scenario,
    Criteria,
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
        )

        return extract_json_from_md(response["content"])

    gpt5 = EvaluationModel(name="GPT-5", execute_prompt=execute_gpt5)

    # Sonnet 4
    def execute_sonnet4(prompt: str) -> str:
        response = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Sonnet_4_Thinking,
        )

        return extract_json_from_md(response["content"])

    sonnet = EvaluationModel(name="Sonnet-4", execute_prompt=execute_sonnet4)

    # Gemini 2.5 Pro
    def execute_gemini(prompt: str) -> str:
        response = ask_model(
            messages=[AIMessage(role="user", content=[TextAIMessageContent(text=prompt)])],
            system_prompt="",
            model=Model.Gemini_25_Pro_0605,
        )

        return extract_json_from_md(response["content"])

    gemini = EvaluationModel(name="Gemini-2.5-Pro", execute_prompt=execute_gemini)

    return [gpt5, sonnet, gemini]


def save_grading_report(grading_path: Path, report: List[dict[str, Any]]):
    """Save the grading report to a file, updating if it exists."""
    new_df = pd.DataFrame(report)

    if grading_path.exists():
        # Read existing report
        try:
            existing_df = pd.read_csv(grading_path)
            # Concatenate with new data and remove duplicates
            combined_df = pd.concat([existing_df, new_df])
            combined_df.to_csv(grading_path, index=False)
            print(f"Updated existing grading report at {grading_path}")
        except Exception as e:
            print(f"Error reading existing report: {e}. Creating a new one.")
            new_df.to_csv(grading_path, index=False)
    else:
        # Create new report if it doesn't exist
        new_df.to_csv(grading_path, index=False)
        print(f"Created new grading report at {grading_path}")


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


def evaluate_scenario_and_store_reports(
    base_path: Path,
    output: str,
    category_criteria_path: Path,
    evaluation_model: EvaluationModel,
) -> Tuple[str, str]:
    """
    Evaluate a single scenario from a dataset.

    This function gets the scenario data, evaluates completeness and accuracy,
    and grades the evaluation reports.

    Args:
        base_path (Path): The base path to the scenario file.
        output (str): The output of the scenario to evaluate.
        category_criteria_path (Path): The path to the criteria file.
        evaluation_model (BaseLanguageModel): The AI model used for evaluation.
        grading_model (BaseLanguageModel): The AI model used for grading.

    Returns:
        Tuple[EvaluationResult, EvaluationResult]: A tuple containing the
        accuracy and completeness evaluation results.
    """

    criteria_yaml: str = read_file(category_criteria_path)
    criteria = Criteria.from_yaml(criteria_yaml)
    scenario_name = criteria.metadata.category

    print(f"Evaluating scenario {scenario_name} with {evaluation_model.name}")

    (accuracy_report, completeness_report) = evaluate_scenario(
        criteria,
        output,
        evaluation_model.execute_prompt,
    )

    try:
        write_file(
            os.path.join(base_path, f"{scenario_name}_{evaluation_model.name}_completeness.md"),
            completeness_report,
        )
    except FileNotFoundError:
        print(f"Scenario directory not found: {scenario_name}. Skipping completeness report.")
    except OSError as e:
        print(f"Failed to write completeness report for scenario {scenario_name}: {e}")

    try:
        write_file(
            os.path.join(base_path, f"{scenario_name}_{evaluation_model.name}_accuracy.md"),
            accuracy_report,
        )
    except FileNotFoundError:
        print(f"Scenario directory not found: {scenario_name}. Skipping accuracy report.")
    except OSError as e:
        print(f"Failed to write accuracy report for scenario {scenario_name}: {e}")

    return accuracy_report, completeness_report


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
        print(f"File {summary_path} does not exist.")
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

        if pd.notna(acc) and pd.notna(comp) and not force_reevaluate:
            print(f"Skipping {category_name} as it already has results.")
            continue

        for root, dirs, files in os.walk(base_path / experiment_type):
            if category_name in dirs:
                category_path = Path(root) / category_name
                category_criteria_path = criteria_path / experiment_type / f"{category_name}_criteria.yaml"

                if not category_criteria_path.exists():
                    print(f"File {category_criteria_path} does not exist.")
                    continue

                output = extract_content(category_path / f"{category_name}_report_1.md")

                if not output:
                    print(f"Scenario {category_name} has no output. Skipping evaluation.")
                    continue

                print(f"Evaluating scenario {category_name}...")

                def process_evaluation_model(
                    evaluation_model,
                ) -> Tuple[str, float, float]:  # model name, accuracy, completeness
                    accuracy_cell_model_name = f"Accuracy_{evaluation_model.name}"
                    completeness_cell_model_name = f"Completeness_{evaluation_model.name}"

                    acc_model, comp_model = row.get(accuracy_cell_model_name, None), row.get(
                        completeness_cell_model_name, None
                    )

                    if pd.notna(acc_model) and pd.notna(comp_model) and not force_reevaluate:
                        print(
                            f"Skipping grading for {category_name} by {evaluation_model.name} as it already has results."
                        )
                        return (evaluation_model.name, acc_model, comp_model)

                    (accuracy_report, completeness_report) = evaluate_scenario_and_store_reports(
                        category_path, output, category_criteria_path, evaluation_model
                    )
                    (accuracy_grading, completeness_grading) = grade_scenario(accuracy_report, completeness_report)

                    # Return results for updating summary_report
                    return (
                        evaluation_model.name,
                        round(accuracy_grading.get_score(), 2),
                        round(completeness_grading.get_score(), 2),
                    )

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [
                        executor.submit(process_evaluation_model, evaluation_model)
                        for evaluation_model in evaluation_models
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        model_name, acc_score, comp_score = future.result()
                        summary_report.at[index, f"Accuracy_{model_name}"] = acc_score
                        summary_report.at[index, f"Completeness_{model_name}"] = comp_score

                # calculate average accuracy and completeness by models evaluations
                summary_report.at[index, "Accuracy"] = round(
                    summary_report.loc[index, [f"Accuracy_{model.name}" for model in evaluation_models]].mean(), 2
                )

                summary_report.at[index, "Completeness"] = round(
                    summary_report.loc[index, [f"Completeness_{model.name}" for model in evaluation_models]].mean(),
                    2,
                )

                summary_report.to_csv(summary_path, index=False)


if __name__ == "__main__":
    evaluate(Model.Gemini_25_Pro_0605, "JS")

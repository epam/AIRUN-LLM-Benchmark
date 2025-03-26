import sys
import os
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_google_vertexai.model_garden import ChatAnthropicVertex

from Utils.llm.config import Model

load_dotenv()

sys.path.append(os.getenv('AUTO_LLM_EVAL_PATH'))
from evaluator import read_file, write_file, evaluate_metric, grade_metric, EvaluationResult

results_path = Path(os.getenv('RESULTS_REPO_PATH')).resolve()
criteria_path = Path(__file__).resolve().parent.parent / 'Scenarios' / 'Criteria' / 'JS'


def get_evaluation_models() -> tuple[ChatAnthropicVertex, ChatOpenAI]:
    """Get the evaluator model."""

    # Define Claude 3.7 with enabled thinking mode
    sonnet = ChatAnthropicVertex(
        model_name="claude-3-7-sonnet@20250219",
        project=os.getenv('GCLOUD_PROJECT_ID'),
        location="us-east5",
        max_token=8192,
        model_kwargs={  # Enable Thinking Mode
            "thinking": {
                "type": "enabled",
                "budget_tokens": 4096
            }
        }
    )

    # Define OpenAI o3-mini model
    o3mini = ChatOpenAI(
        model="o3-mini",
        temperature=1
    )

    # deepseek_r1 = AzureChatOpenAI(
    #     temperature=1,
    #     azure_deployment="deepseek-r1",
    #     model="deepseek-r1",
    #     azure_endpoint=os.getenv('AZURE_DEPLOYMENT_BASE_URL'),
    #     api_version="2024-05-01-preview",
    #     max_tokens=8096,
    #     api_key=os.getenv('AZURE_DEPLOYMENT_KEY')
    # )

    return sonnet, o3mini


def get_grading_model() -> ChatOpenAI:
    """Get the grading model."""

    # Define GPT-4-omni model
    model = ChatOpenAI(
        model="gpt-4o-2024-11-20",
        logprobs=True,
        top_logprobs=5,
        temperature=0,  # request deterministic behavior
    )

    return model


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
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to find content between "### Answer:\n" and "\n### Tokens:"
    pattern = re.compile(r"### Answer:\n(.*?)\n### Tokens:", re.DOTALL)
    match = pattern.search(content)

    if match:
        return match.group(1).strip()
    else:
        return ""


def evaluate_scenario(
        base_path: Path,
        output: str,
        category_criteria_path: Path,
        evaluation_model: ChatOpenAI | AzureChatOpenAI,
        grading_model: ChatOpenAI
) -> Tuple[EvaluationResult, EvaluationResult]:
    """
    Evaluate a single scenario from a dataset.

    This function gets the scenario data, evaluates completeness and accuracy,
    and grades the evaluation reports.

    Args:
        base_path (Path): The base path to the scenario file.
        output (str): The output of the scenario to evaluate.
        category_criteria_path (Path): The path to the criteria file.
        evaluation_model (ChatAnthropicVertex, ChatOpenAI): The AI model used for evaluation.
        grading_model (ChatOpenAI): The AI model used for grading.

    Returns:
        Tuple[EvaluationResult, EvaluationResult]: A tuple containing the
        accuracy and completeness evaluation results.
    """

    metadata_content: str = read_file(category_criteria_path)

    metadata: Dict[str, Any] = yaml.safe_load(metadata_content)
    meta: Dict[str, Any] = metadata.get("metadata", {})
    meta["model"] = evaluation_model.model_name
    scenario_name = meta.get("category")
    evaluation_steps: Dict[str, List[str]] = metadata.get("evaluation_steps", {})

    completeness_evaluation_steps: List[str] = evaluation_steps.get("completeness", [])
    accuracy_evaluation_steps: List[str] = evaluation_steps.get("accuracy", [])

    print(f"Evaluating scenario {scenario_name} with {evaluation_model.model_name}")

    completeness_report = evaluate_metric(
        completeness_evaluation_steps, output, evaluation_model
    )

    try:
        write_file(
            os.path.join(base_path, f"{scenario_name}_{evaluation_model.model_name}_completeness.md"),
            completeness_report,
        )
    except FileNotFoundError:
        print(f"Scenario directory not found: {scenario_name}. Skipping completeness report.", )
    except OSError as e:
        print(f"Failed to write completeness report for scenario {scenario_name}: {e}")

    accuracy_report = evaluate_metric(
        accuracy_evaluation_steps, output, evaluation_model
    )

    try:
        write_file(
            os.path.join(base_path, f"{scenario_name}_{evaluation_model.model_name}_accuracy.md"),
            accuracy_report,
        )
    except FileNotFoundError:
        print(f"Scenario directory not found: {scenario_name}. Skipping accuracy report.", )
    except OSError as e:
        print(f"Failed to write accuracy report for scenario {scenario_name}: {e}")

    print(f"Grading scenario {scenario_name} with {grading_model.model_name}")
    accuracy: EvaluationResult = grade_metric(
        accuracy_report, grading_model
    )
    accuracy.set_metadata(meta)

    completeness: EvaluationResult = grade_metric(
        completeness_report, grading_model
    )
    completeness.set_metadata(meta)

    return accuracy, completeness


def main(model_name: Model, language: str = "JS"):
    """
    Main function to evaluate the scenarios.

    This function evaluates the scenarios for a given model and language.
    It loads the evaluation and grading models, reads the summary file,
    and evaluates the scenarios based on the criteria.

    Args:
        model_name (Model): The name of the model.
        language (str): The programming language of scenarios.

    Returns:
        None
    """

    evaluation_models = get_evaluation_models()
    grading_model = get_grading_model()

    grading_report = []

    base_path = results_path / "Output" / f"{model_name}" / language
    grading_path = base_path / "grading.csv"
    summary_path = base_path / "summary.csv"

    if not summary_path.exists():
        print(f"File {summary_path} does not exist.")
        return

    summary_report = pd.read_csv(summary_path)
    for index, row in summary_report.iterrows():
        experiment_type = row['Type']
        category = row['Category']
        dataset = row['Dataset'] if row['Dataset'] != 'none' else ''
        complexity = row['Complexity'] if row['Complexity'] != 'none' else ''
        size = row['Size'] if row['Size'] != 'none' else ''
        category_name = construct_category_name(category, dataset, complexity, size)

        acc, comp = row.get("Accuracy", None), row.get("Completeness", None)

        if not (pd.isna(acc) or pd.isna(comp)):
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

                for evaluation_model in evaluation_models:
                    accuracy_cell_model_name = f"Accuracy_{evaluation_model.model_name}"
                    completeness_cell_model_name = f"Completeness_{evaluation_model.model_name}"

                    acc_model, comp_model = row.get(accuracy_cell_model_name, None), row.get(completeness_cell_model_name, None)

                    if not (pd.isna(acc_model) or pd.isna(comp_model)):
                        print(f"Skipping evaluation for {category_name} by {evaluation_model.model_name} as it already has results.")
                        continue

                    (accuracy, completeness) = evaluate_scenario(
                        category_path, output, category_criteria_path, evaluation_model, grading_model
                    )

                    accuracy_data = accuracy.to_data_frame("accuracy")
                    grading_report.append(accuracy_data)

                    completeness_data = completeness.to_data_frame("completeness")
                    grading_report.append(completeness_data)

                    # add the normalized results to the summary
                    summary_report.at[index, accuracy_cell_model_name] = round(accuracy_data["weighted_score"] - 1, 2)
                    summary_report.at[index, completeness_cell_model_name] = round(completeness_data["weighted_score"] - 1, 2)

                # calculate average accuracy and completeness by models evaluations
                summary_report.at[index, "Accuracy"] = round(
                    summary_report.loc[index, [f"Accuracy_{model.model_name}" for model in evaluation_models]].mean(), 2
                )

                summary_report.at[index, "Completeness"] = round(
                    summary_report.loc[index, [f"Completeness_{model.model_name}" for model in evaluation_models]].mean(), 2
                )

                summary_report.to_csv(summary_path, index=False)

    save_grading_report(grading_path, grading_report)


if __name__ == "__main__":
    main(Model.Gemini_20_Pro_0205, "JS")

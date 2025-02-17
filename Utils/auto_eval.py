import sys
import os
import re
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

sys.path.append(os.getenv('AUTO_LLM_EVAL_PATH'))
from evaluator import evaluate_scenario

results_path = Path(os.getenv('RESULTS_REPO_PATH')).resolve()
criteria_path = Path(__file__).resolve().parent.parent / 'Scenarios' / 'Criteria'


def get_model():
    """Get the evaluator model."""

    # Define GPT-4-omni model
    model = ChatOpenAI(
        model="gpt-4o-2024-05-13",
        temperature=0,  # request deterministic behavior
    )

    return model


def save_grading_report(report_path: str, report):
    """Save the grading report to a file."""
    df = pd.DataFrame(report)
    df.to_csv(report_path, index=False)


def construct_category_name(category, dataset, complexity, size):
    parts = [category]
    if dataset:
        parts.append(dataset)
    if complexity:
        parts.append(complexity)
    if size:
        parts.append(size)
    return "_".join(parts)


def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to find content between "### Answer:\n" and "\n### Tokens:"
    pattern = re.compile(r'### Answer:\n(.*?)\n### Tokens:', re.DOTALL)
    match = pattern.search(content)

    if match:
        return match.group(1).strip()
    else:
        return None


def main(model_name, language="JS"):
    """Main function to evaluate the scenarios."""
    gpt_4_omni = get_model()
    grading_report = []

    base_path = results_path / "Output" / model_name / language
    report_path = base_path / "grading.csv"
    summary_path = base_path / "summary.csv"

    if not summary_path.exists():
        print(f"File {summary_path} does not exist.")
        return

    df = pd.read_csv(summary_path)
    for index, row in df.iterrows():
        experiment = row['Experiment']
        category = row['Category']
        dataset = row['Dataset'] if row['Dataset'] != 'none' else ''
        complexity = row['Complexity'] if row['Complexity'] != 'none' else ''
        size = row['Size'] if row['Size'] != 'none' else ''
        category_name = construct_category_name(category, dataset, complexity, size)

        for root, dirs, files in os.walk(base_path / experiment):
            if category_name in dirs:
                category_path = Path(root) / category_name
                category_criteria_path = criteria_path / language / experiment / f'{category_name}_criteria.yaml'

                if not category_criteria_path.exists():
                    print(f"File {category_criteria_path} does not exist.")
                    continue

                output = extract_content(category_path / f'{category_name}_report_1.md')

                (accuracy, completeness) = evaluate_scenario(
                    category_path, output, category_criteria_path, gpt_4_omni
                )

                accuracy_data = accuracy.to_data_frame("accuracy")
                grading_report.append(accuracy_data)

                completeness_data = completeness.to_data_frame("completeness")
                grading_report.append(completeness_data)

                # add the normalized results to the summary
                df.at[index, 'Accuracy'] = round(accuracy_data['weighted_score'] - 1, 2)
                df.at[index, 'Completeness'] = round(completeness_data['weighted_score'] - 1, 2)

    df.to_csv(summary_path, index=False)
    save_grading_report(report_path, grading_report)


if __name__ == "__main__":
    main('ChatGPT4o_august_0509', 'JS')

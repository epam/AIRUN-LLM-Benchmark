import os
from pathlib import Path


def traverse_files_and_get_content(repo_path: str):
    """
    Traverses all files in a repository and returns their content as a formatted string.
    """
    output = []
    for subdir, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(file_path, repo_path)
            extension = file.split('.')[-1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output.append(f'```{extension}\n'
                              f'// {relative_path}\n'
                              f'{content}\n```\n')
                print(f'Reading {relative_path}')
            except UnicodeDecodeError:
                print(f'Can\'t read file {file_path}, it\'s not a text file')
    return "\n".join(output)


def extract_dataset_name(task_file_name: str, base_dataset: str):
    """
    Extracts dataset name from task file name.
    For example: "WriteTestsForActualCode_ReactSelect_extra_high_high.md" -> "ReactSelect"
    """
    # Get all dataset names
    dataset_names = os.listdir(base_dataset) or []

    # Check if any dataset name appears as a substring in the task file name
    for dataset in dataset_names:
        if dataset in task_file_name:
            return dataset

    return None


def enrich_task_with_dataset(task_file_path: str, output_dir: str, base_dataset_path: str):
    """
    Reads a task file, identifies the dataset to use, and creates an enriched version
    with the dataset files included.
    """
    # Extract task file name and get dataset name
    task_file_name = os.path.basename(task_file_path)
    dataset_name = extract_dataset_name(task_file_name, base_dataset_path)

    if not dataset_name:
        print(f"Could not determine dataset for {task_file_name}, skipping...")
        return

    # Read task file
    with open(task_file_path, 'r', encoding='utf-8') as f:
        task_content = f.read()

    # Get dataset path
    dataset_path = os.path.join(base_dataset_path, dataset_name)

    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"Dataset {dataset_name} not found at {dataset_path}, skipping...")
        return

    # Get dataset content
    dataset_content = traverse_files_and_get_content(dataset_path)

    # Replace placeholder with dataset content
    enriched_content = task_content.replace("<place_code_here>", dataset_content)

    # Create output directory if it doesn't exist
    task_dir = os.path.dirname(task_file_path)
    rel_path = os.path.relpath(task_dir, os.path.join(Path(__file__).resolve().parent.parent, "Scenarios", "Tasks"))
    output_task_dir = os.path.join(output_dir, rel_path)
    os.makedirs(output_task_dir, exist_ok=True)

    # Write enriched content to output file
    output_file_path = os.path.join(output_task_dir, task_file_name)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(enriched_content)

    print(f"Successfully enriched {task_file_name} with {dataset_name} dataset")


def enrich_tasks(language: str = "JS"):
    """
    Main function to process all task files.
    """
    base_path = Path(__file__).resolve().parent.parent
    tasks_path = base_path / "Scenarios" / "Tasks" / language
    output_dir = base_path / "Scenarios" / "Tasks_Enriched"
    base_dataset_path = base_path / "Dataset" / language

    os.makedirs(output_dir, exist_ok=True)

    # Track successfully enriched files
    enriched_count = 0

    # Walk through all tasks
    for subdir, dirs, files in os.walk(tasks_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(subdir, file)
                enrich_task_with_dataset(file_path, str(output_dir), str(base_dataset_path))
                enriched_count += 1

    print(f"Completed: Enriched {enriched_count} task files")


if __name__ == "__main__":
    enrich_tasks()

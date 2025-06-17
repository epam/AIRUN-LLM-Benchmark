import os
import re
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
            extension = file.split(".")[-1]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                output.append(f"```{extension}\n" f"// {relative_path}\n" f"{content}\n```\n")
            except UnicodeDecodeError:
                print(f"Can't read file {file_path}, it's not a text file")
    return "\n".join(output)


def enrich_task_content(task_name: str, task_content: str, datasets_categoty: Path) -> str:
    """
    Enriches the task content by replacing the <source_code> tag with the content of the
    corresponding repository (from datasets) specified in the <place_code_here repo="REPO_NAME"/> tag.
    If the repository does not exist or is not a directory, skips the enrichment.
    """
    code_placement_pattern = r'<place_code_here\s+repo="([^"]+)"\s*\/>'
    match = re.search(
        code_placement_pattern,
        task_content,
    )
    if match:
        repo_name = match.group(1)
        repo_path = datasets_categoty / repo_name
        if repo_path.exists() and repo_path.is_dir():
            repo_content = traverse_files_and_get_content(str(repo_path))
            enriched_content = re.sub(
                code_placement_pattern,
                lambda _m: repo_content,  # to avoid backslash eacaping issues
                task_content,
                count=1,
            )
            return enriched_content
        else:
            print(f"Enrich task {task_name}: repository {repo_name} not found in datasets category, skipping...")
            return task_content
    else:
        return task_content

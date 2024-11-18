import os
import re
import sys


def create_file(output_dir, file_name, file_content):
    full_path = os.path.join(root_path, output_dir, file_name)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(file_content.strip())


def process_react(answer_content, output_dir):
    code_blocks = re.findall(r"```[\s\S]*?```", answer_content)
    for block in code_blocks:
        block_content = block[3:-3].strip()
        type_of_file, first_line, file_content = block_content.split('\n', 2)
        file_name = first_line.replace('// ', '')
        if type_of_file == "css":
            continue
        if type_of_file == "html":
            file_name = first_line.split(' ')[1]

        create_file(output_dir, file_name, file_content)


def process_angular(answer_content, output_dir):
    file_blocks = answer_content.split('\n\n**')[1:]
    for block in file_blocks:
        file_name, code = block.split('**\n', 1)
        block_content = code[3:-3].strip()
        type_of_file, file_content = block_content.split('\n', 1)

        if type_of_file == "css":
            continue
        create_file(output_dir, file_name, file_content)


def extract_and_write_files(md_file_path: str):
    if not md_file_path: return
    directory_path = os.path.dirname(md_file_path)
    output_dir = os.path.basename(directory_path)
    with open(md_file_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()
    answer_content = content.split("### Answer:")[-1]

    process_react(answer_content, output_dir)
    # process_angular(answer_content, output_dir)


root_path = '<folder-name>'

paths = [
    'path-to-answer'
]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_and_write_files(sys.argv[1])
    else:
        for path in paths:
            extract_and_write_files(path)
        print('Exit')
        exit(1)

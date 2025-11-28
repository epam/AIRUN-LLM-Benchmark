from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
import json

from Utils.llm.ai_message import AIMessageContentFactory, AIMessageContent


class ToolHandler(ABC):
    """Abstract base class for tool handlers"""

    @abstractmethod
    def handle(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str, **kwargs) -> "AIMessageContent":
        """Handle a tool call and return appropriate messages"""
        pass


class ListFilesHandler(ToolHandler):
    """Handler for list_files tool"""

    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path

    def handle(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str, **kwargs) -> "AIMessageContent":
        try:
            file_list = self._list_files(self.dataset_path)
            files_content = "\n".join(file_list)
            return AIMessageContentFactory.create_tool_response(tool_name, files_content, tool_id)
        except Exception as e:
            error_content = f"Error: Could not list files directory files"
            return AIMessageContentFactory.create_text(error_content)

    def _list_files(self, base_path: Path) -> List[str]:
        """List all files in the directory"""
        file_list = []
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(base_path)
                file_list.append(str(relative_path))
        return file_list


class ReadFileHandler(ToolHandler):
    """Handler for read_file tool"""

    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path

    def handle(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str, **kwargs) -> "AIMessageContent":
        file_path = tool_args["file_path"]
        full_path = self.dataset_path / file_path

        try:
            with open(full_path, "r") as file:
                file_content = file.read()
                return AIMessageContentFactory.create_tool_response(tool_name, file_content, tool_id)
        except FileNotFoundError:
            error_content = f"Error: File at {file_path} not found or file_path is incorrect."
            return AIMessageContentFactory.create_tool_response(tool_name, error_content, tool_id)


class WriteFileHandler(ToolHandler):
    """Handler for write_file tool"""

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def handle(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str, **kwargs) -> "AIMessageContent":
        file_path = tool_args["file_path"]
        content = tool_args["content"]
        full_path = self.output_path / file_path.lstrip("/")

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as file:
                if ".json" in file_path:
                    json.dump(content, file, indent=4)
                else:
                    file.write(content)

            return AIMessageContentFactory.create_tool_response(tool_name, "File written successfully", tool_id)
        except IOError as e:
            print(f"Failed to write file at {file_path}. Error: {e}")
            return AIMessageContentFactory.create_tool_response(tool_name, "Failed to write file", tool_id)


class FileStructureHandler(ToolHandler):
    """Handler for file_structure tool"""

    def handle(self, tool_name: str, tool_args: Dict[str, Any], tool_id: str, **kwargs) -> "AIMessageContent":
        # Add success response
        return AIMessageContentFactory.create_tool_response(
            tool_name,
            "File structure received successfully. Now provide each file from this list",
            tool_id,
        )


class ToolHandlerFactory:
    """Factory for creating tool handlers"""

    @staticmethod
    def create_handler(tool_name: str, dataset_path: Path, output_path: Path) -> ToolHandler:
        """Create appropriate handler for the given tool"""
        handlers = {
            "list_files": ListFilesHandler(dataset_path),
            "read_file": ReadFileHandler(dataset_path),
            "write_file": WriteFileHandler(output_path),
            "file_structure": FileStructureHandler(),
        }

        if tool_name not in handlers:
            raise ValueError(f"Unknown tool: {tool_name}")

        return handlers[tool_name]

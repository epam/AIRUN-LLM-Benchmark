import base64


class AIMessageContent:
    pass


class TextAIMessageContent(AIMessageContent):
    text: str

    def __init__(self, text: str):
        super().__init__()
        self.text = text


class ImageAIMessageContent(AIMessageContent):
    file_name: str
    binary_content: bytes

    def __init__(
        self,
        file_name: str,
        binary_content: bytes,
    ):
        super().__init__()
        self.file_name = file_name
        self.binary_content = binary_content

    def to_base64_url(self) -> str:
        base64_str = base64.b64encode(self.binary_content).decode("utf-8")
        file_extension = self.file_name.split(".")[-1]
        if file_extension.lower() in ["jpg", "jpeg"]:
            mime_type = "image/jpeg"
        elif file_extension.lower() == "png":
            mime_type = "image/png"
        elif file_extension.lower() == "gif":
            mime_type = "image/gif"
        else:
            raise ValueError(f"Unsupported image format: {file_extension}")

        return f"data:{mime_type};base64,{base64_str}"


class AIMessage:
    role: str
    content_list: list[AIMessageContent]

    def __init__(self, role: str, content_list: list[AIMessageContent]):
        self.role = role
        self.content_list = content_list

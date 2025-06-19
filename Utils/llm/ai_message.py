import base64


class AIMessageContent:
    def to_dict(self):
        pass


class TextAIMessageContent(AIMessageContent):
    text: str

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def to_dict(self):
        return self.text


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

    def media_type(self) -> str:
        file_extension = self.file_name.split(".")[-1].lower()
        if file_extension in ["jpg", "jpeg"]:
            return "image/jpeg"
        elif file_extension == "png":
            return "image/png"
        elif file_extension == "gif":
            return "image/gif"
        else:
            raise ValueError(f"Unsupported image format: {file_extension}")

    def to_base64(self) -> str:
        return base64.b64encode(self.binary_content).decode("utf-8")

    def to_base64_url(self) -> str:
        return f"data:{self.media_type()};base64,{self.to_base64()}"

    def to_dict(self):
        return self.file_name


class AIMessage:
    role: str
    content: list[AIMessageContent]

    def __init__(self, role: str, content: list[AIMessageContent]):
        self.role = role
        self.content = content

    def to_dict(self):
        return {
            "role": self.role,
            "content": [c.to_dict() for c in self.content]
        }

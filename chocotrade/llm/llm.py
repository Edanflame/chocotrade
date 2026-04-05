import re

from openai import OpenAI

from ..base.plugin import Plugin


class LLMCore(Plugin):
    """"""
    def __init__(self):
        super().__init__()
        self.client: OpenAI = None
        self.base_url: str = None
        self.model: str = None
        self.api_key: str = None

        self.history = [
            {
                "role": "system",
                "content":
                """
                你是一个量化助手，请你把回复分成两块内容，对话部分正常回复，\
                你发送的代码部分始终用 ```python ... ``` 进行包裹。
                """
            }
        ]

    def init(self):
        """"""
        config = self.load_config("robot", "standard-llm")
        base_url = config.get("base_url")
        api_key = config.get("api_key")
        self.model = config.get("model_name")
        # self.client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except Exception:
            pass

    def ask(self, user_input):
        """
        非流式输出方法：等待大模型全部生成后一次性返回。
        """
        self.history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=False  # 设置为 False，一次性返回
        )

        full_reply = response.choices[0].message.content

        # 记录记忆
        self.history.append({"role": "assistant", "content": full_reply})

        return full_reply

    def ask_stream(self, user_input):
        """
        流式输出方法：生成器，逐字返回。
        """
        self.history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=True
        )

        full_reply = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                full_reply += content
                yield content

        self.history.append({"role": "assistant", "content": full_reply})

    @staticmethod
    def extract_code(text):
        """通用静态方法：从回复中筛选 Python 代码块"""
        pattern = r"```(?:python|py)?\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return "\n\n".join(matches) if matches else ""

    def clear(self):
        """清空对话历史"""
        self.history = [self.history[0]]

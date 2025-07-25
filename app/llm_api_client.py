import logging
from enum import Enum
from typing import Generic, TypeVar

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

T = TypeVar('T')


class Model(Enum):
    GPT_4_1_mini: str = "gpt-4.1-mini"
    GPT_4o: str = "gpt-4o"
    GPT_o3_mini_high: str = "gpt-o3-mini-high"


class LlmApiClient[T]:
    def __init__(self, api_key: str, model_name: Model = Model.GPT_4o) -> None:
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name.value,
            temperature=0.5
        )

    def create_response(self, prompt: ChatPromptTemplate, schema: dict, dto_class: type[T]) -> T:
        try:
            structured_llm = self.llm.with_structured_output(schema=schema)
            chain = prompt | structured_llm
            response: dict = chain.invoke({})
        except Exception as e:
            logging.error(f"Ошибка при запросе к модели {e}")
            response: dict = {}

        return dto_class.from_dict(response)

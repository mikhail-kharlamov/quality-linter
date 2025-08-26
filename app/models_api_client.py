import logging
from enum import Enum
from typing import TypeVar

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.callbacks.manager import get_openai_callback

T = TypeVar('T')


class LlmModel(Enum):
    GPT_4_1_mini: str = "gpt-4.1-mini"
    GPT_4o: str = "gpt-4o"
    GPT_o3_mini: str = "o3-mini"
    GPT_5_nano: str = "gpt-5-nano"


class EmbeddingModel(Enum):
    TEXT_EMB_3_small: str = "text-embedding-3-small"
    TEXT_EMB_3_large: str = "text-embedding-3-large"
    TEXT_EMB_ada_002: str = "text-embedding-ada-002"



class ModelsApiClient[T]:
    def __init__(self, api_key: str, llm_model_name: LlmModel = LlmModel.GPT_4o,
                 embedding_model_name: EmbeddingModel = EmbeddingModel.TEXT_EMB_3_small) -> None:
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=llm_model_name.value
        )

        self.embedding_model = OpenAIEmbeddings(
            api_key=api_key,
            model=embedding_model_name
        )

        self.total_cost: float = 0.0

    def create_response_for_llm(self, dto_class: type[T], prompt: ChatPromptTemplate, schema: dict = None) -> T:
        try:
            with get_openai_callback() as cb:
                if schema:
                    structured_llm = self.llm.with_structured_output(
                        schema=schema,
                        method = "json_schema",
                        strict=True
                    )
                    chain = prompt | structured_llm
                    response: dict = chain.invoke({})
                else:
                    chain = prompt | self.llm
                    message = chain.invoke({})
                    response: dict = {"content": message.content}

            self.total_cost += cb.total_cost
            logging.info(f"Total cost: {self.total_cost} USD")
        except Exception as e:
            logging.error(f"Ошибка при запросе к модели {e}")
            response: dict = {}

        return dto_class.from_dict(response)

    def embed(self, text: str) -> list[float]:
        try:
            embedding: list[float] = self.embedding_model.embed_query(text)
        except Exception as e:
            logging.error(f"Ошибка при получении эмбеддингов: {e}")
            embedding = []

        return embedding

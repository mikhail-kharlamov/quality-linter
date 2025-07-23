import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dtos import AutoReviewDto


class LlmApiClient:
    def __init__(self, api_key: str, model_name: str = "gpt-4o") -> None:
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.5
        )

    def create_response(self, prompt: ChatPromptTemplate, schema: dict) -> AutoReviewDto:
        try:
            structured_llm = self.llm.with_structured_output(schema=schema)
            chain = prompt | structured_llm
            response = chain.invoke({})
            text = json.dumps(response)
        except Exception as e:
            logging.error(f"Ошибка при запросе к модели {e}")
            text = "{}"

        return AutoReviewDto.from_json(text)

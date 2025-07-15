from dtos import DirectoryDto, CriteriaDto, AutoReviewDto
from app.llm_api_client import LlmApiClient
from app.parser import Parser
from load_dotenv import load_dotenv
import os


class Reviewer:
    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        self.llm_api_client = LlmApiClient(api_key=api_key, model_name=model_name)
        self.parser = Parser()

    def __validate(self, review: AutoReviewDto, criteria: CriteriaDto) -> bool:
        return True

    def review(self, path_to_code: str, criteria: CriteriaDto) -> AutoReviewDto:
        directory: DirectoryDto = self.parser.parse_directory(path_to_code)
        result: AutoReviewDto = self.llm_api_client.get_review(directory=directory, criteria=criteria)
        if not self.__validate(result, criteria):
            raise ValueError("Review does not meet the specified criteria")
        return result

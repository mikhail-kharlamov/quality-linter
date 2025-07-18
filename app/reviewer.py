from app.llm_api_client import LlmApiClient
from app.parser import Parser
from dtos import AutoReviewDto, CriteriaDto, DirectoryDto


class Reviewer:
    def __init__(self, llm_api_client: LlmApiClient, parser: Parser) -> None:
        self.llm_api_client = llm_api_client
        self.parser = parser

    def __validate(self, review: AutoReviewDto, criteria: CriteriaDto) -> bool:
        return criteria.min_mark <= review.mark <= criteria.max_mark

    def review(self, path_to_code: str, criteria: CriteriaDto) -> AutoReviewDto:
        #directory: DirectoryDto = self.parser.parse_directory(path_to_code)
        directory: DirectoryDto = self.parser.get_directory_from_json(path_to_code)
        result: AutoReviewDto = self.llm_api_client.get_review(directory=directory, criteria=criteria)
        if not self.__validate(result, criteria):
            raise ValueError("Review does not meet the specified criteria")
        return result

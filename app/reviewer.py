from pathlib import Path

from app.llm_api_client import LlmApiClient
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from dtos import AutoReviewDto, CriteriaDto, DirectoryDto
from json_schema import JsonSchemaLoader


class Reviewer:
    def __init__(self, llm_api_client: LlmApiClient, parser: Parser,
                 prompt_builder: PromptBuilder) -> None:
        self.prompt_builder = prompt_builder
        self.llm_api_client = llm_api_client
        self.parser = parser

    def review(self, path_to_code: Path, criteria: CriteriaDto) -> AutoReviewDto:
        #directory: DirectoryDto = self.parser.parse_directory(path_to_code)
        directory: DirectoryDto = self.parser.get_directory_from_json(str(path_to_code), enumerate_code_lines=True)

        prompt = self.prompt_builder.build_prompt(
            system_prompt_url="system/code_review_system.j2",
            human_prompt_url="human/code_review_human.j2",
            directory=directory,
            criteria=criteria
        )
        schema = JsonSchemaLoader.get_schema(criteria)

        result: AutoReviewDto = self.llm_api_client.create_response(
            prompt=prompt,
            schema=schema,
            dto_class=AutoReviewDto
        )
        return result

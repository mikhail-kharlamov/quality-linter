import logging
from pathlib import Path

from app.models_api_client import ModelsApiClient
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from dtos import CodeReviewDto, CriteriaDto, DirectoryDto
from json_schema import JsonSchemaLoader


class Reviewer:
    def __init__(self, llm_api_client: ModelsApiClient, parser: Parser,
                 prompt_builder: PromptBuilder) -> None:
        self.prompt_builder = prompt_builder
        self.llm_api_client = llm_api_client
        self.parser = parser

    def review(self, directory: DirectoryDto, criteria: CriteriaDto) -> CodeReviewDto:
        file_texts = self.parser.parse_directory_dto(directory)

        prompt = self.prompt_builder.build_system_and_human_prompt(
            system_prompt_url="reviewer/system/code_review_system.j2",
            human_prompt_url="reviewer/human/code_review_human.j2",
            system_vars=criteria.to_dict(),
            human_vars={"directory_json": file_texts}
        )
        schema = JsonSchemaLoader.get_review_schema(criteria)

        result: CodeReviewDto = self.llm_api_client.create_response_for_llm(
            prompt=prompt,
            schema=schema,
            dto_class=CodeReviewDto
        )
        return result

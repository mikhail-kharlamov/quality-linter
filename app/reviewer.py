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

    def review(self, path_to_directory: Path, code_file: str, criteria: CriteriaDto) -> CodeReviewDto:
        #directory: DirectoryDto = self.parser.parse_directory(path_to_code)
        path_to_code = path_to_directory / code_file
        directory: DirectoryDto = self.parser.get_directory_from_json(str(path_to_code), enumerate_code_lines=True)

        file_texts = self.parser.parse_directory_dto(directory)

        prompt = self.prompt_builder.build_prompt(
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

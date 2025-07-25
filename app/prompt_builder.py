from jinja2 import Environment, FileSystemLoader
from langchain_core.prompts import ChatPromptTemplate

from dtos import CriteriaDto, DirectoryDto


class PromptBuilder:
    def __init__(self, templates_dir: str) -> None:
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
            trim_blocks=True
        )

    def build_prompt(self, system_prompt_url: str, human_prompt_url: str,
                     directory: DirectoryDto, criteria: CriteriaDto) -> ChatPromptTemplate:
        system_msg = self.env.get_template(system_prompt_url).render(criteria.to_dict()).replace('{',
                                                                '{{').replace('}', '}}')
        human_msg = self.env.get_template(human_prompt_url).render({"directory_json": directory.to_json()}).replace('{',
                                                                '{{').replace('}', '}}')

        return ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", human_msg)
        ])

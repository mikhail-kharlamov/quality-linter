from jinja2 import Environment, FileSystemLoader
from langchain_core.prompts import ChatPromptTemplate


class PromptBuilder:
    def __init__(self, templates_dir: str) -> None:
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
            trim_blocks=True
        )

    def build_prompt(self, system_prompt_url: str, human_prompt_url: str, human_vars: dict,
                     system_vars: dict = None) -> ChatPromptTemplate:
        if system_vars:
            system_msg = self.env.get_template(system_prompt_url).render(system_vars).replace('{',
                                                                    '{{').replace('}', '}}')
        else:
            system_msg = self.env.get_template(system_prompt_url).render()

        human_msg = self.env.get_template(human_prompt_url).render(human_vars).replace('{',
                                                                '{{').replace('}', '}}')

        return ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", human_msg)
        ])

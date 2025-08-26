from unittest.mock import MagicMock, patch

import pytest
from langchain_core.prompts import ChatPromptTemplate

from app.prompt_builder import PromptBuilder


class TestPromptBuilder:
    @pytest.fixture
    def builder(self, tmp_path):
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        system_template = templates_dir / "system.j2"
        system_template.write_text("System: {{ var1 }}")

        human_template = templates_dir / "human.j2"
        human_template.write_text("Human: {{ var2 }}")

        return PromptBuilder(str(templates_dir))

    def test_init(self):
        templates_dir = "test_dir"

        mock_loader = MagicMock()
        mock_env = MagicMock()

        with patch('app.prompt_builder.FileSystemLoader', return_value=mock_loader) as mock_loader_cls, \
                patch('app.prompt_builder.Environment', return_value=mock_env) as mock_env_cls:
            PromptBuilder(templates_dir)

            mock_loader_cls.assert_called_once_with(templates_dir)
            mock_env_cls.assert_called_once_with(
                loader=mock_loader,
                autoescape=True,
                trim_blocks=True
            )

    def test_build_prompt_with_vars(self, builder):
        prompt = builder.build_system_and_human_prompt(
            system_prompt_url="system.j2",
            human_prompt_url="human.j2",
            human_vars={"var2": "value2"},
            system_vars={"var1": "value1"}
        )

        assert isinstance(prompt, ChatPromptTemplate)

    def test_build_prompt_without_system_vars(self, builder):
        prompt = builder.build_system_and_human_prompt(
            system_prompt_url="system.j2",
            human_prompt_url="human.j2",
            human_vars={"var2": "value2"}
        )

        assert isinstance(prompt, ChatPromptTemplate)

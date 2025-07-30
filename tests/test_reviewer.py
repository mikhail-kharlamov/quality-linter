from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.reviewer import Reviewer
from dtos import CodeReviewDto, CriteriaDto, DirectoryDto


class TestReviewer:
    @pytest.fixture
    def mock_models_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_parser(self):
        return MagicMock()

    @pytest.fixture
    def mock_prompt_builder(self):
        return MagicMock()

    @pytest.fixture
    def reviewer(self, mock_models_client, mock_parser, mock_prompt_builder):
        return Reviewer(
            llm_api_client=mock_models_client,
            parser=mock_parser,
            prompt_builder=mock_prompt_builder
        )

    def test_review(self, reviewer, mock_parser, mock_prompt_builder, mock_models_client):
        test_dir = Path("test_dir")
        test_file = "file.json"
        test_criteria = CriteriaDto(error_types=["type1", "type2"])

        mock_dir_dto = DirectoryDto(content=[])
        mock_parser.get_directory_from_json.return_value = mock_dir_dto
        mock_parser.parse_directory_dto.return_value = "parsed content"

        mock_prompt = MagicMock()
        mock_prompt_builder.build_prompt.return_value = mock_prompt

        test_review = CodeReviewDto(mark=90, comments=[])
        mock_models_client.create_response_for_llm.return_value = test_review

        result = reviewer.review(test_dir, test_file, test_criteria)

        assert result == test_review
        mock_parser.get_directory_from_json.assert_called_once_with(
            str(test_dir / test_file), enumerate_code_lines=True
        )
        mock_parser.parse_directory_dto.assert_called_once_with(mock_dir_dto)
        mock_prompt_builder.build_prompt.assert_called_once()

        assert mock_models_client.create_response_for_llm.call_count == 1
        call_args = mock_models_client.create_response_for_llm.call_args
        assert call_args.kwargs['dto_class'] == CodeReviewDto
        assert call_args.kwargs['prompt'] == mock_prompt
        assert isinstance(call_args.kwargs['schema'], dict)

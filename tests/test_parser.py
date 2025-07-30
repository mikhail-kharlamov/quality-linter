import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from app.parser import Parser
from dtos import DirectoryDto, FileDto


class TestParser:
    @pytest.fixture
    def parser(self):
        return Parser()

    def test_parse_directory_dto(self, parser):
        dir_dto = DirectoryDto(
            content=[
                FileDto(path="file1.txt", content="content1", is_binary=False),
                DirectoryDto(
                    content=[
                        FileDto(path="sub/file2.txt", content="content2", is_binary=False)
                    ]
                )
            ]
        )

        result = parser.parse_directory_dto(dir_dto)

        assert "file1.txt:\ncontent1" in result
        assert "sub/file2.txt:\ncontent2" in result

    def test_get_directory_from_json(self, parser):
        test_data = [
            {"path": "file1.txt", "content": "test", "is_binary": False},
            {"path": "file2.txt", "content": "test2", "is_binary": True}
        ]

        m = mock_open(read_data=json.dumps(test_data))
        with patch('builtins.open', m):
            result = parser.get_directory_from_json("test.json")

            assert len(result.content) == 2
            assert isinstance(result.content[0], FileDto)
            assert result.content[0].path == "file1.txt"
            assert result.content[1].is_binary

    def test_enumerate_lines(self, parser):
        text = "line1\nline2\nline3"
        result = parser._enumerate_lines(text)

        assert result == "1 line1\n2 line2\n3 line3"

    def test_is_binary_file_by_extension(self, parser):
        with patch('pathlib.Path.suffix', new_callable=lambda: '.exe'):
            path = Path("test.exe")
            assert parser._is_binary_file(path) is True

    def test_is_binary_file_by_content(self, parser):
        test_data = b'\x00\x01\x02\x03' + b' ' * 1020

        m = mock_open()
        m.return_value.read.return_value = test_data

        with patch('builtins.open', m):
            path = Path("test.bin")
            assert parser._is_binary_file(path) is True

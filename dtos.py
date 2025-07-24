from dataclasses import dataclass, field
from typing import Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CommentDto:
    path: str
    start_line: int
    end_line: int
    body: str
    original_start_line: int = field(default=0)
    original_end_line: int = field(default=0)


@dataclass_json
@dataclass
class FileDto:
    name: str = field(default="")
    extension: str = field(default="")
    is_binary: bool = field(default=False)
    path: str = field(default="")
    content: str = field(default="")


@dataclass_json
@dataclass
class DirectoryDto:
    name: str = field(default="")
    path: str = field(default="")
    content: list[Union[FileDto, 'DirectoryDto']] = field(default_factory=list)


@dataclass_json
@dataclass
class AutoReviewDto:
    mark: int = field(default=0)
    comments: list[CommentDto] = field(default_factory=list)


@dataclass_json
@dataclass
class CriteriaDto:
    min_mark: int = field(default=0)
    max_mark: int = field(default=100)

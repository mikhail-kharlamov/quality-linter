from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from dataclasses_json import dataclass_json


class Type(Enum):
    Missing_Property_Usage: str = "Missing Property Usage"
    Naming_Convention_Violation: str = "Naming Convention Violation"
    Insufficient_Test_Coverage: str = "Insufficient Test Coverage"
    Missing_StyleCop_Usage: str = "Missing StyleCop Usage"
    Missing_License_Header: str = "Missing License Header"
    Namespace_Organization_Issue: str = "Namespace Organization Issue"
    Expression_bodied_Method_Opportunity: str = "Expression-bodied Method Opportunity"
    XML_Tag_Syntax_Errors: str = "XML Tag Syntax Errors"
    Resource_Management_Issue: str = "Resource Management Issue"


@dataclass_json
@dataclass
class CommentDto:
    path: str
    error_type: str
    start_line: int
    end_line: int
    body: str
    prepared_text: str = field(default="")
    embedding: list[float] = field(default_factory=list)
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
class CodeReviewDto:
    mark: int = field(default=0)
    comments: list[CommentDto] = field(default_factory=list)


@dataclass_json
@dataclass
class CriteriaDto:
    error_types: list[str]
    min_mark: int = field(default=0)
    max_mark: int = field(default=100)


@dataclass_json
@dataclass
class FileMetricDto:
    number: int = field(default=0)
    precision: float = field(default=0.0)
    recall: float = field(default=0.0)


@dataclass_json
@dataclass
class BenchmarkDto:
    precision: float = field(default=0.0)
    recall: float = field(default=0.0)
    files_metrics: list[FileMetricDto] = field(default_factory=list)


@dataclass_json
@dataclass
class DataPreparingDto:
    content: str

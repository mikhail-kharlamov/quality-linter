from dataclasses import dataclass, field
from typing import Union

from dataclasses_json import dataclass_json
from enum import Enum


class Type(Enum):
    Code_Style_Violation: str = "Code Style Violation"
    Missing_Property_Usage: str = "Missing Property Usage"
    Compiler_Warnings: str = "Compiler Warnings"
    Lack_of_Input_Validation: str = "Lack of Input Validation"
    Naming_Convention_Violation: str = "Naming Convention Violation"
    Insufficient_Test_Coverage: str = "Insufficient Test Coverage"
    Missing_StyleCop_Usage: str = "Missing StyleCop Usage"
    Missing_License_Header: str = "Missing License Header"
    Namespace_Organization_Issue: str = "Namespace Organization Issue"
    Expression_bodied_Method_Opportunity: str = "Expression-bodied Method Opportunity"
    XML_Tag_Syntax_Errors: str = "XML Tag Syntax Errors"
    Resource_Management_Issue: str = "Resource Management Issue"
    Incorrect_Project_Type: str = "Incorrect Project Type"
    Type_Safety_Concern: str = "Type Safety Concern"
    Unused_Variable: str = "Unused Variable"
    Undocumented_Return_Values: str = "Undocumented Return Values"
    Code_Duplication: str = "Code Duplication"
    Algorithm_Complexity_Issue: str = "Algorithm Complexity Issue"
    Incorrect_Access_Modifiers: str = "Incorrect Access Modifiers"
    Unnecessary_Files_in_PR: str = "Unnecessary Files in PR"
    Using_Directive_Placement: str = "Using Directive Placement"
    Unnecessary_Setter: str = "Unnecessary Setter"
    Non_specific_Exception_Throwing: str = "Non-specific Exception Throwing"
    Constructor_Logic_Placement: str = "Constructor Logic Placement"
    Missing_Exception_Constructors: str = "Missing Exception Constructors"
    Race_Condition: str = "Race Condition"
    Threading_Optimization: str = "Threading Optimization"
    Concurrency_Issue: str = "Concurrency Issue"
    Test_Organization_Issue: str = "Test Organization Issue"
    Missing_Test_Attributes: str = "Missing Test Attributes"
    Incorrect_Interface_Implementation: str = "Incorrect Interface Implementation"
    Memory_Leak_Potential: str = "Memory Leak Potential"
    Test_Assertion_Clarity: str = "Test Assertion Clarity"
    Insufficient_Thread_Testing: str = "Insufficient Thread Testing"
    Visibility_Modifier_Missing: str = "Visibility Modifier Missing"
    Unnecessary_Public_Type: str = "Unnecessary Public Type"
    Magic_Number_Usage: str = "Magic Number Usage"
    Incorrect_Recursion_Usage: str = "Incorrect Recursion Usage"
    Missing_Documentation: str = "Missing Documentation"
    Private_Property_Misuse: str = "Private Property Misuse"
    Unclear_Method_Naming: str = "Unclear Method Naming"
    Incorrect_Exception_Type: str = "Incorrect Exception Type"
    Unnecessary_Class: str = "Unnecessary Class"
    Incorrect_Loop_Structure: str = "Incorrect Loop Structure"
    Algorithm_Optimization_Opportunity: str = "Algorithm Optimization Opportunity"
    Test_Data_Organization: str = "Test Data Organization"


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
class GroupedCommentsDto:
    Code_Style_Violation: list[CommentDto] = field(default_factory=list)
    Missing_Property_Usage: list[CommentDto] = field(default_factory=list)
    Compiler_Warnings: list[CommentDto] = field(default_factory=list)
    Lack_of_Input_Validation: list[CommentDto] = field(default_factory=list)
    Naming_Convention_Violation: list[CommentDto] = field(default_factory=list)
    Insufficient_Test_Coverage: list[CommentDto] = field(default_factory=list)
    Missing_StyleCop_Usage: list[CommentDto] = field(default_factory=list)
    Missing_License_Header: list[CommentDto] = field(default_factory=list)
    Namespace_Organization_Issue: list[CommentDto] = field(default_factory=list)
    Expression_bodied_Method_Opportunity: list[CommentDto] = field(default_factory=list)
    XML_Tag_Syntax_Errors: list[CommentDto] = field(default_factory=list)
    Resource_Management_Issue: list[CommentDto] = field(default_factory=list)
    Incorrect_Project_Type: list[CommentDto] = field(default_factory=list)
    Type_Safety_Concern: list[CommentDto] = field(default_factory=list)
    Unused_Variable: list[CommentDto] = field(default_factory=list)
    Undocumented_Return_Values: list[CommentDto] = field(default_factory=list)
    Code_Duplication: list[CommentDto] = field(default_factory=list)
    Algorithm_Complexity_Issue: list[CommentDto] = field(default_factory=list)
    Incorrect_Access_Modifiers: list[CommentDto] = field(default_factory=list)
    Unnecessary_Files_in_PR: list[CommentDto] = field(default_factory=list)
    Using_Directive_Placement: list[CommentDto] = field(default_factory=list)
    Unnecessary_Setter: list[CommentDto] = field(default_factory=list)
    Non_specific_Exception_Throwing: list[CommentDto] = field(default_factory=list)
    Constructor_Logic_Placement: list[CommentDto] = field(default_factory=list)
    Missing_Exception_Constructors: list[CommentDto] = field(default_factory=list)
    Race_Condition: list[CommentDto] = field(default_factory=list)
    Threading_Optimization: list[CommentDto] = field(default_factory=list)
    Concurrency_Issue: list[CommentDto] = field(default_factory=list)
    Test_Organization_Issue: list[CommentDto] = field(default_factory=list)
    Missing_Test_Attributes: list[CommentDto] = field(default_factory=list)
    Incorrect_Interface_Implementation: list[CommentDto] = field(default_factory=list)
    Memory_Leak_Potential: list[CommentDto] = field(default_factory=list)
    Test_Assertion_Clarity: list[CommentDto] = field(default_factory=list)
    Insufficient_Thread_Testing: list[CommentDto] = field(default_factory=list)
    Visibility_Modifier_Missing: list[CommentDto] = field(default_factory=list)
    Unnecessary_Public_Type: list[CommentDto] = field(default_factory=list)
    Magic_Number_Usage: list[CommentDto] = field(default_factory=list)
    Incorrect_Recursion_Usage: list[CommentDto] = field(default_factory=list)
    Missing_Documentation: list[CommentDto] = field(default_factory=list)
    Private_Property_Misuse: list[CommentDto] = field(default_factory=list)
    Unclear_Method_Naming: list[CommentDto] = field(default_factory=list)
    Incorrect_Exception_Type: list[CommentDto] = field(default_factory=list)
    Unnecessary_Class: list[CommentDto] = field(default_factory=list)
    Incorrect_Loop_Structure: list[CommentDto] = field(default_factory=list)
    Algorithm_Optimization_Opportunity: list[CommentDto] = field(default_factory=list)
    Test_Data_Organization: list[CommentDto] = field(default_factory=list)


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


@dataclass_json
@dataclass
class FileDiffDto:
    file_path: str
    diff: str


@dataclass_json
@dataclass
class PullRequestDiffDto:
    diffs: list[FileDiffDto] = field(default_factory=list)

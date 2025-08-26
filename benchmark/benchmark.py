import json
import logging
from enum import Enum
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from app.models_api_client import ModelsApiClient
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from app.reviewer import Reviewer
from dtos import BenchmarkDto, CodeReviewDto, CommentDto, CriteriaDto, DataPreparingDto, FileMetricDto


class Autor(Enum):
    HUMAN: str = "human"
    MODEL: str = "model"


#error_types = [
#    "Code Style Violation",
#    "Missing Property Usage",
#    "Compiler Warnings",
#    "Lack of Input Validation",
#    "Naming Convention Violation",
#    "Insufficient Test Coverage",
#    "Missing StyleCop Usage",
#    "Missing License Header",
#    "Namespace Organization Issue",
#    "Expression-bodied Method Opportunity",
#    "XML Tag Syntax Errors",
#    "Resource Management Issue",
#    "Incorrect Project Type",
#    "Type Safety Concern",
#    "Unused Variable",
#    "Undocumented Return Values",
#    "Code Duplication",
#    "Algorithm Complexity Issue",
#    "Incorrect Access Modifiers",
#    "Unnecessary Files in PR",
#    "Using Directive Placement",
#    "Unnecessary Setter",
#    "Non-specific Exception Throwing",
#    "Constructor Logic Placement",
#    "Missing Exception Constructors",
#    "Race Condition",
#    "Threading Optimization",
#    "Concurrency Issue",
#    "Test Organization Issue",
#    "Missing Test Attributes",
#    "Incorrect Interface Implementation",
#    "Memory Leak Potential",
#    "Test Assertion Clarity",
#    "Insufficient Thread Testing",
#    "Visibility Modifier Missing",
#    "Unnecessary Public Type",
#    "Magic Number Usage",
#    "Incorrect Recursion Usage",
#    "Missing Documentation",
#    "Private Property Misuse",
#    "Unclear Method Naming",
#    "Incorrect Exception Type",
#    "Unnecessary Class",
#    "Incorrect Loop Structure",
#    "Algorithm Optimization Opportunity",
#    "Test Data Organization",
#    "Unknown Error Type"
#]
#error_types = ['Code Style Violation',
#               'Missing Property Usage',
#               'Compiler Warnings',
#               'Naming Convention Violation',
#               'Insufficient Test Coverage',
#               'Missing StyleCop Usage',
#               'Missing License Header',
#               'Namespace Organization Issue',
#               'Expression-bodied Method Opportunity',
#               'XML Tag Syntax Errors',
#               'Resource Management Issue',
#               'Test Organization Issue',
#               'Visibility Modifier Missing',
#               'Unnecessary Public Type',
#               'Magic Number Usage',
#               'Incorrect Recursion Usage',
#               'Missing Documentation',
#               'Private Property Misuse',
#               'Unclear Method Naming',
#               'Incorrect Exception Type',
#               'Unnecessary Class']
error_types = ['Algorithm Optimization Opportunity',
               'Visibility Modifier Missing',
               'Unclear Method Naming',
               'Test Organization Issue',
               'Expression-bodied Method Opportunity',
               'Insufficient Test Coverage',
               'Unnecessary Public Type',
               'Incorrect Exception Type',
               'Algorithm Complexity Issue',
               'Missing Property Usage',
               'Magic Number Usage',
               'Missing Documentation',
               'Resource Management Issue',
               'Naming Convention Violation',
               'Namespace Organization Issue']


class Benchmark:
    def __init__(self, reviewer: Reviewer, prompt_builder: PromptBuilder,
                 models_api_client: ModelsApiClient, similarity_threshold: float) -> None:
        self.reviewer = reviewer
        self.models_api_client = models_api_client
        self.prompt_builder = prompt_builder
        self.similarity_threshold = similarity_threshold

        self.type_recall = dict(zip(error_types, [0] * len(error_types), strict=False))
        self.type_precision = dict(zip(error_types, [[[i, 0] for i in range(1, 101)] for _ in error_types], strict=False))
        self.type_other_types = dict(
            zip(error_types, [dict([[error_type, 0] for error_type in error_types]) for _ in error_types], strict=False))

    def __prepare_human_comment(self, comment_text: str) -> str:
        prompt = self.prompt_builder.build_system_and_human_prompt(
            system_prompt_url="benchmark/system/preparing_comment_system.j2",
            human_prompt_url="benchmark/human/preparing_comment_human.j2",
            human_vars={"human_comment": comment_text}
        )

        prepared_comment = self.models_api_client.create_response_for_llm(
            prompt=prompt,
            dto_class=DataPreparingDto
        )

        return prepared_comment.content

    def __code_review_enrichment(self, code_review_json: dict, autor: Autor) -> CodeReviewDto:
        code_review = CodeReviewDto.from_dict(code_review_json)
        for comment in code_review.comments:
            prepared_text = self.__prepare_human_comment(comment.body) if autor.value == "human" else comment.body
            comment_embedding: list[float] = self.models_api_client.embed(prepared_text)

            comment.prepared_text = prepared_text
            comment.embedding = comment_embedding

        return code_review

    def __get_and_save_review(self, path_to_dataset: Path,
                              dataset_length: int, criteria: CriteriaDto) -> list[tuple[CodeReviewDto, CodeReviewDto]]:
        reviews = []

        for i in range(1, dataset_length + 1):
            logging.error(f"Обработка пул-реквеста {i}")
            if i in [13, 43, 44, 53, 67, 85, 87]:
                logging.warning(f"Пропуск ревью {i}")
                continue
            path = path_to_dataset / f"file_{i}"

            with open(path / "code-review-typed.json", encoding="utf-8") as f:
                code_review_comments = json.load(f)
                comments = [comment for comment in code_review_comments if comment["error_type"] in error_types]
                if len(comments) == 0:
                    logging.warning(f"Нет комментариев в ревью {i}, пропуск ревью")
                    continue
                code_review_json = {"mark": 50, "comments": code_review_comments}
                human_review = self.__code_review_enrichment(code_review_json, Autor.HUMAN)
                logging.info(f"Ревью {i} обогащено стандартизированным комментарием и эмбеддингом")
                filtered_human_review = CodeReviewDto(
                    mark=human_review.mark,
                    comments=[
                        comment for comment in human_review.comments
                        if comment.error_type in error_types
                    ]
                )

            with open(path / "code-review-enriched-4.json", 'w', encoding="utf-8") as f:
                try:
                    json.dump(filtered_human_review.to_dict(), f, ensure_ascii=False, indent=4)
                    logging.info(f"Reviewing {i} file")
                except ValueError as e:
                    logging.error(f"Review Error: {e}")
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")

            with open(path / "auto-review-4.json", 'w', encoding="utf-8") as f:
                try:
                    parser = Parser()
                    directory = parser.get_directory_from_json(str(path / "code.json"), enumerate_code_lines=True)
                    auto_review_json = self.reviewer.review(directory, criteria).to_dict()
                except ValueError as e:
                    logging.error(e)
                    continue
                auto_review = self.__code_review_enrichment(auto_review_json, Autor.MODEL)
                auto_review_enriched_json = auto_review.to_dict()
                logging.info(f"Автоматическое ревью {i} обогащено эмбеддингом")

                try:
                    json.dump(auto_review_enriched_json, f, ensure_ascii=False, indent=4)
                    logging.info(f"Reviewing {i} file")
                except ValueError as e:
                    logging.error(f"Review Error: {e}")
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")

            with open(path / "auto-review-for-view-4.json", 'w', encoding="utf-8") as f:
                try:
                    json.dump(auto_review_json, f, ensure_ascii=False, indent=4)
                    logging.info(f"Reviewing {i} file")
                except ValueError as e:
                    logging.error(f"Review Error: {e}")
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")

            reviews.append((auto_review, filtered_human_review))
            logging.info(f"Обработано {i} ревью")

        logging.info(f"Обработано {len(reviews)} ревью")
        return reviews

    def evaluate(self, path: Path, dataset_length: int) -> BenchmarkDto:
        logging.info("Start benchmarking...")
        path_to_dataset = path / "dataset"
        criteria = CriteriaDto(min_mark=0, max_mark=100, error_types=error_types)

        reviews: list[tuple[CodeReviewDto, CodeReviewDto]] = self.__get_and_save_review(path_to_dataset, dataset_length,
                                                                                        criteria)

        tp_for_all, fn_for_all = 0, 0
        unused_comments_for_all = []
        benchmark_dto = BenchmarkDto()

        file_number = 0
        negative_metrics = []
        for auto_review, human_review in reviews:
            file_number += 1
            if file_number in [13, 43, 44, 53, 67, 85, 87]:
                file_number += 1
            if len(human_review.comments) == 0:
                logging.warning(f"Нет комментариев в ревью {file_number}, пропуск ревью")
                continue
            logging.info(f"Ревью файла: {human_review.comments[0].path}")
            files_metric_dto = FileMetricDto(number=file_number)

            tp_for_file, fn_for_file = 0, 0
            unused_comments_for_file = auto_review.comments.copy()
            similar = 0

            for human_comment in human_review.comments:
                logging.info(f"Обработка комментария: {human_comment.body}")
                logging.info(f"Обработанный текст комментария: {human_comment.prepared_text}")
                group: list[CommentDto] = auto_review.comments
                for model_comment in group:
                    similarity: float = cosine_similarity(
                        [human_comment.embedding],
                        [model_comment.embedding]
                    )[0][0]
                    logging.info(f"Сравнение с комментарием: {model_comment.body}")
                    logging.info(f"Схожесть комментариев: {similarity}")
                    if similarity >= self.similarity_threshold:
                        similar += 1
                        if model_comment in unused_comments_for_file:
                            del unused_comments_for_file[unused_comments_for_file.index(model_comment)]
                        if model_comment in unused_comments_for_file:
                            del unused_comments_for_file[unused_comments_for_file.index(model_comment)]
                        if human_comment.error_type == model_comment.error_type:
                            self.type_recall[human_comment.error_type] += 1
                        else:
                            self.type_other_types[human_comment.error_type][model_comment.error_type] += 1
                if similar != 0:
                    tp_for_file += 1
                else:
                    fn_for_file += 1
            unused_comments_for_all.extend(unused_comments_for_file)
            tp_for_all += tp_for_file
            fn_for_all += fn_for_file

            for unused in unused_comments_for_file:
                self.type_precision[unused.error_type][file_number][1] += 1

            if (tp_for_file + fn_for_file) == 0:
                logging.warning(f"Неопределенные метрики на файле {file_number}, пропуск файла (recall)")
                continue
            if (tp_for_file + len(unused_comments_for_file)) == 0:
                logging.warning(f"Неопределенные метрики на файле {file_number}, пропуск файла (precision)")
                continue
            files_metric_dto.recall = tp_for_file / (tp_for_file + fn_for_file)
            files_metric_dto.precision = tp_for_file / (tp_for_file + len(unused_comments_for_file))

            logging.info(f"На файле {file_number} recall {files_metric_dto.recall}, precision {files_metric_dto.precision}")
            logging.info(f"Общий recall {tp_for_all / (tp_for_all + fn_for_all)}, precision {tp_for_all / (tp_for_all + len(unused_comments_for_all))}")

            if files_metric_dto.recall < 0.001 or files_metric_dto.precision < 0.001:
                negative_metrics.append(file_number)

            benchmark_dto.files_metrics.append(files_metric_dto)

        benchmark_dto.recall = tp_for_all / (tp_for_all + fn_for_all)
        benchmark_dto.precision = tp_for_all / (tp_for_all + len(unused_comments_for_all))

        logging.info(f"Нулевые метрики на файлах с номерами: {negative_metrics}")

        with open(path_to_dataset / "type_recall-4.json", 'w', encoding="utf8") as f:
            try:
                json.dump(self.type_recall, f, ensure_ascii=False, indent=4)
            except ValueError as e:
                logging.error(f"Review Error: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

        with open(path_to_dataset / "type_precision-4.json", 'w', encoding="utf8") as f:
            try:
                json.dump(self.type_precision, f, ensure_ascii=False, indent=4)
            except ValueError as e:
                logging.error(f"Review Error: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

        with open(path_to_dataset / "type_other_types-4дщЂ21111.json", 'w', encoding="utf8") as f:
            try:
                json.dump(self.type_other_types, f, ensure_ascii=False, indent=4)
            except ValueError as e:
                logging.error(f"Review Error: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

        return benchmark_dto

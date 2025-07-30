import json
import logging
from enum import Enum
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from app.models_api_client import ModelsApiClient
from app.prompt_builder import PromptBuilder
from app.reviewer import Reviewer
from dtos import CriteriaDto, CodeReviewDto, GroupedCommentsDto, Type, CommentDto, BenchmarkDto, FileMetricDto, \
    DataPreparingDto


class Autor(Enum):
    HUMAN: str = "human"
    MODEL: str = "model"


class Benchmark:
    def __init__(self, reviewer: Reviewer, prompt_builder: PromptBuilder,
                 models_api_client: ModelsApiClient[CodeReviewDto], similarity_threshold: float) -> None:
        self.reviewer = reviewer
        self.models_api_client = models_api_client
        self.prompt_builder = prompt_builder
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def __group_comments_by_type(code_review: CodeReviewDto) -> GroupedCommentsDto:
        groups = dict([(comment_type.name, []) for comment_type in Type])
        for comment in code_review.comments:
            groups[comment.error_type.replace(" ", "_").replace("-", "_")].append(comment)
        return GroupedCommentsDto.from_dict(groups)


    def __prepare_human_comment(self, comment_text: str) -> str:
        prompt = self.prompt_builder.build_prompt(
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
            comment_embedding: list[float] = self.models_api_client.get_embedding(prepared_text)

            comment.prepared_text = prepared_text
            comment.embedding = comment_embedding

        return code_review

    def __get_and_save_review(self, path_to_dataset: Path,
                              dataset_length: int, criteria: CriteriaDto) -> list[tuple[CodeReviewDto, CodeReviewDto]]:
        reviews = []

        for i in range(1, dataset_length + 1):
            path = path_to_dataset / f"file_{i}"

            with open(path / "auto-review-benchmark-3.json", 'w', encoding="utf-8") as f:
                auto_review_json = self.reviewer.review(path, "code.json",
                                                        "diffs.txt", criteria).to_dict()
                auto_review = self.__code_review_enrichment(auto_review_json, Autor.MODEL)
                auto_review_enriched_json = auto_review.to_dict()

                try:
                    json.dump(auto_review_enriched_json, f, ensure_ascii=False, indent=4)
                    logging.info(f"Reviewing {i} file")
                except ValueError as e:
                    logging.error(f"Review Error: {e}")
                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")

            with open(path / "code-review.json", 'r', encoding="utf-8") as f:
                code_review_comments = json.load(f)
                code_review_json = {"mark": 50, "comments": code_review_comments}
                human_review = self.__code_review_enrichment(code_review_json, Autor.HUMAN)

            reviews.append((auto_review, human_review))

        return reviews

    def evaluate(self, path_to_dataset: Path, dataset_length: int) -> BenchmarkDto:
        criteria = CriteriaDto(min_mark=0, max_mark=100, error_types=[member.value for member in Type])

        reviews: list[tuple[CodeReviewDto, CodeReviewDto]] = self.__get_and_save_review(path_to_dataset, dataset_length,
                                                                                        criteria)

        tp_for_all, fn_for_all = 0, 0
        unused_comments_for_all = []
        benchmark_dto = BenchmarkDto()

        file_number = 0
        for auto_review, human_review in reviews:
            logging.debug(f"Ревью файла: {human_review.comments[0].path}")
            file_number += 1
            files_metric_dto = FileMetricDto(number=file_number)

            tp_for_file, fn_for_file = 0, 0
            unused_comments_for_file = auto_review.comments.copy()
            similar = 0

            grouped_auto_review: GroupedCommentsDto = Benchmark.__group_comments_by_type(auto_review)

            for human_comment in human_review.comments:
                group_name = human_comment.error_type.replace(" ", "_").replace("-", "_")
                logging.debug(f"Обработка комментария: {human_comment.body}")
                logging.debug(f"Обработанный текст комментария: {human_comment.prepared_text}")
                #group: list[CommentDto] = getattr(grouped_auto_review, group_name)
                group: list[CommentDto] = auto_review.comments
                for model_comment in group:
                    similarity: float = cosine_similarity(
                        [human_comment.embedding],
                        [model_comment.embedding]
                    )[0][0]
                    logging.debug(f"Сравнение с комментарием: {model_comment.body}")
                    logging.debug(f"Схожесть комментариев: {similarity}")
                    if similarity >= self.similarity_threshold:
                        similar += 1
                        if model_comment in unused_comments_for_file:
                            del unused_comments_for_file[unused_comments_for_file.index(model_comment)]
                if similar != 0:
                    tp_for_file += 1
                else:
                    fn_for_file += 1
            unused_comments_for_all.extend(unused_comments_for_file)
            tp_for_all += tp_for_file
            fn_for_all += fn_for_file

            files_metric_dto.recall = tp_for_file / (tp_for_file + fn_for_file)
            files_metric_dto.precision = tp_for_file / (tp_for_file + len(unused_comments_for_file))

            benchmark_dto.files_metrics.append(files_metric_dto)

        benchmark_dto.recall = tp_for_all / (tp_for_all + fn_for_all)
        benchmark_dto.precision = tp_for_all / (tp_for_all + len(unused_comments_for_all))

        return benchmark_dto

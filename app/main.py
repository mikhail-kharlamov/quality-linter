import logging
import os
from logging import Formatter
from pathlib import Path

from colorlog import ColoredFormatter
from load_dotenv import load_dotenv

from app.github_api_client import GitHubApiClient
from app.models_api_client import EmbeddingModel, LlmModel, ModelsApiClient
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from app.reviewer import Reviewer
from benchmark.benchmark import Benchmark
from dtos import BenchmarkDto, PullRequestDto, FileDto, DirectoryDto, CriteriaDto


def set_logger() -> None:
    console_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    file_formatter = Formatter(
        "%(asctime)s - %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler('application.log')
    file_handler.setFormatter(file_formatter)

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def evaluate_benchmark(reviewer: Reviewer, prompt_builder: PromptBuilder,
                       models_api_client: ModelsApiClient, path_to_code: Path) -> None:
    benchmark = Benchmark(
        reviewer=reviewer,
        prompt_builder=prompt_builder,
        models_api_client=models_api_client,
        similarity_threshold=0.6
    )

    benchmark_dto: BenchmarkDto = benchmark.evaluate(
        path=path_to_code,
        dataset_length=100
    )

    logging.info(f"Dataset metrics: recall {benchmark_dto.recall}, precision {benchmark_dto.precision}")
    for file_metric in benchmark_dto.files_metrics:
        logging.info(
            f"File {file_metric.number} metrics: recall {file_metric.recall}, precision {file_metric.precision}")

    logging.info(f"угаданные правильно: {benchmark.type_recall}")
    logging.info(f"галлюцинации: {benchmark.type_precision}")
    logging.info(f"покрытия другими типами: {benchmark.type_other_types}")


def main() -> None:
    set_logger()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    models_api_client = ModelsApiClient(api_key=api_key, llm_model_name=LlmModel.GPT_5_nano,
                                     embedding_model_name=EmbeddingModel.TEXT_EMB_3_large)
    parser = Parser()
    prompt_builder = PromptBuilder("../prompts")
    reviewer = Reviewer(llm_api_client=models_api_client,
                        parser=parser,
                        prompt_builder=prompt_builder)

    github_api_client = GitHubApiClient(
        token=os.getenv("GITHUB_ACCESS_TOKEN")
    )

    pr = PullRequestDto(
        owner="mikhail-kharlamov",
        repo="CSharp-Homeworks",
        pull_number=13
    )

    files: list[FileDto] = github_api_client.get_pull_request_content(pr)
    directory = DirectoryDto(
        content=files
    )
    criteria = CriteriaDto(min_mark=0, max_mark=100, error_types=error_types)

    code_review = reviewer.review(directory, criteria)

    github_api_client.post_comments_for_pull_request(
        pull_request=pr,
        comments=code_review.comments,
    )


if __name__ == "__main__":
    main()

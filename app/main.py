import json
import logging
from logging import Formatter, Filter
import os
from pathlib import Path

from colorlog import ColoredFormatter
from load_dotenv import load_dotenv

from app.models_api_client import ModelsApiClient, LlmModel, EmbeddingModel
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from app.reviewer import Reviewer
from benchmark.benchmark import Benchmark


def set_logger():
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

    file_handler = logging.FileHandler('application-partial.log')
    file_handler.setFormatter(file_formatter)

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


def delete():
    paths_to_code = Path("/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/dataset")
    for i in range(1, 11):
        path = paths_to_code / f"file_{i}/auto-review-benchmark-3.json"
        path.unlink(missing_ok=True)
    log_path = Path("/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/app/application-3.log")
    log_path.unlink(missing_ok=True)


def main():
    set_logger()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    models_api_client = ModelsApiClient(api_key=api_key, llm_model_name=LlmModel.GPT_o3_mini,
                                     embedding_model_name=EmbeddingModel.TEXT_EMB_3_large)
    parser = Parser()
    #parser.parse_diffs(Path("/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/dataset/file_1/diffs.txt"))
    prompt_builder = PromptBuilder("../prompts")
    reviewer = Reviewer(llm_api_client=models_api_client,
                        parser=parser,
                        prompt_builder=prompt_builder)

    paths_to_code = Path("/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/few-shot-dataset")
    benchmark = Benchmark(
        reviewer=reviewer,
        prompt_builder=prompt_builder,
        models_api_client=models_api_client,
        similarity_threshold=0.7
    )
    print(benchmark.evaluate(paths_to_code, 2))


if __name__ == "__main__":
    main()
    #delete()

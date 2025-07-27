import json
import logging
import os
from pathlib import Path

from colorlog import ColoredFormatter
from load_dotenv import load_dotenv

from app.llm_api_client import LlmApiClient, Model
from app.parser import Parser
from app.prompt_builder import PromptBuilder
from app.reviewer import Reviewer
from dtos import CriteriaDto


def set_logger():
    formatter = ColoredFormatter(
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

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def main():
    set_logger()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    llm_api_client = LlmApiClient(api_key=api_key, model_name=Model.GPT_4o)
    parser = Parser()
    prompt_builder = PromptBuilder("../prompts")
    reviewer = Reviewer(llm_api_client=llm_api_client,
                        parser=parser,
                        prompt_builder=prompt_builder)

    paths_to_code = Path("/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/dataset")
    criteria = CriteriaDto(min_mark=0, max_mark=100)
    for i in range(1, 11):
        path = paths_to_code / f"file_{i}"

        with open(path / "auto-review-with-code-lines-enumeration.json", 'w', encoding="utf-8") as f:
            review_result = reviewer.review(path / "code.json", criteria).to_dict()
            try:
                json.dump(review_result, f, ensure_ascii=False, indent=4)
                logging.info(f"Review Result: {review_result}")
            except ValueError as e:
                logging.error(f"Review Error: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

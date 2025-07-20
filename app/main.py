import json
import os

from load_dotenv import load_dotenv

from app.llm_api_client import LlmApiClient
from app.parser import Parser
from app.reviewer import Reviewer
from dtos import CriteriaDto


def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

    llm_api_client = LlmApiClient(api_key=api_key, model_name=model_name)
    parser = Parser()
    reviewer = Reviewer(llm_api_client=llm_api_client, parser=parser)

    paths_to_code = "/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/dataset/file_"
    criteria = CriteriaDto(min_mark=0, max_mark=100)
    for i in range(1, 11):
        path = paths_to_code + str(i)

        with open(path + "/auto-review.json", 'w', encoding="utf-8") as f:
            review_result = reviewer.review(path + "/code.json", criteria).to_dict()
            try:
                json.dump(review_result, f, ensure_ascii=False, indent=4)
                print("Review Result:", review_result)
            except ValueError as e:
                print("Review Error:", e)
            except Exception as e:
                print("An unexpected error occurred:", e)


if __name__ == "__main__":
    main()

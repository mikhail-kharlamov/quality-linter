from app.reviewer import Reviewer
from dtos import CriteriaDto


def main():
    reviewer = Reviewer()
    path_to_code = "/Users/mikhailkharlamov/Documents/Projects/SummerSchool/quality-linter/app"
    criteria = CriteriaDto(min_mark=0, max_mark=100)
    try:
        review_result = reviewer.review(path_to_code, criteria)
        print("Review Result:", review_result.to_json())
    except ValueError as e:
        print("Review Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__":
    main()

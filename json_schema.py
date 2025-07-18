from dtos import CriteriaDto


class JsonSchemaLoader:
    @staticmethod
    def get_schema(criteria: CriteriaDto) -> dict:
        """
        Returns a JSON schema for automatic code review response.

        :param minimum_mark: Minimum score for the code review.
        :param maximum_mark: Maximum score for the code review.
        :return: JSON schema as a dictionary.
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "AutoReviewDto",
            "description": "Schema for automatic code review response",
            "type": "object",
            "properties": {
                "mark": {
                    "description": "Numeric score for the code review",
                    "type": "integer",
                    "minimum": criteria.min_mark,
                    "maximum": criteria.max_mark
                },
                "comments": {
                    "description": "List of code review comments",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "description": "Path to the file being commented",
                                "type": "string"
                            },
                            "start_line": {
                                "description": "Line number in the file",
                                "type": "integer",
                                "minimum": 0
                            },
                            "end_line": {
                                "description": "Line number in the file",
                                "type": "integer",
                                "minimum": 0
                            },
                            "body": {
                                "description": "The comment text",
                                "type": "string"
                            }
                        },
                        "required": ["path", "start_line", "end_line", "body"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["mark", "comments"],
            "additionalProperties": False
        }

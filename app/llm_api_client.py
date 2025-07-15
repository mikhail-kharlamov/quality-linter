import openai

from dtos import AutoReviewDto, CriteriaDto, DirectoryDto
from json_schema import JsonSchemaLoader


class LlmApiClient:
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name

    def __build_prompt(self, directory: DirectoryDto, criteria: CriteriaDto) -> str:
        prompt: str = (
            f"""Perform a thorough code review of the provided code. Your response MUST be a valid JSON object strictly following this schema:

            {{
              "mark": "integer score (0-100)",
              "comments": [
                {{
                  "path": "file path",
                  "line": "line number",
                  "body": "detailed comment"
                }}
              ]
            }}
            
            Rules:
            1. Score must be {criteria.min_mark}-{criteria.max_mark} (higher is better)
            2. Each comment must specify exact file and line
            3. Focus on critical issues first (bugs, security, performance)
            4. Include constructive suggestions for improvement
            5. Be concise but precise in comments
            
            Example response:
            {{
              "mark": 75,
              "comments": [
                {{
                  "path": "src/main.py",
                  "line": 42,
                  "body": "Potential SQL injection - use parameterized queries"
                }},
                {{
                  "path": "utils/helpers.py",
                  "line": 15,
                  "body": "This loop can be optimized using list comprehension"
                }}
              ]
            }}
            
            Now review this code in the folders and files presented in json format:
            {directory.to_json()}
            
            Provide ONLY the JSON response without any additional commentary or formatting."""
        )
        return prompt

    def __create_response(self, prompt: str, schema: dict) -> str:
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "math_response",
                        "strict": True,
                        "schema": schema
                    },
                },
            )
            text = response.output_text
        except Exception as e:
            text = f"Ошибка при обращении к API OpenAI: {str(e)}"

        return text

    def get_review(self, directory: DirectoryDto, criteria: CriteriaDto) -> AutoReviewDto:
        prompt: str = self.__build_prompt(directory, criteria)
        schema = JsonSchemaLoader.get_schema(criteria)
        response_text: str = self.__create_response(prompt, schema)
        return AutoReviewDto.from_json(response_text)

import os

import openai
from load_dotenv import load_dotenv


class LlmApiClient:
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name

    def create_response(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            text = response.output_text
        except Exception as e:
            text = f"Ошибка при обращении к API OpenAI: {str(e)}"

        return text


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

    client = LlmApiClient(api_key=api_key, model_name=model_name)
    prompt = "Представь, что ты python-разработчик. Напиши алгоритм быстрой сортировки на python"

    print(client.create_response(prompt))

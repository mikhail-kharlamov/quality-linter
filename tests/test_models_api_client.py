from dataclasses import dataclass
from unittest.mock import MagicMock, create_autospec, patch

import pytest
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.models_api_client import EmbeddingModel, LlmModel, ModelsApiClient


@dataclass
class TestDto:
    content: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class TestModelsApiClient:
    @pytest.fixture
    def mock_llm(self):
        mock = create_autospec(ChatOpenAI, instance=True)
        mock.with_structured_output.return_value = MagicMock()
        return mock

    @pytest.fixture
    def mock_embeddings(self):
        mock = create_autospec(OpenAIEmbeddings, instance=True)
        mock.embed_query.return_value = [0.1, 0.2, 0.3]
        return mock

    def test_init(self, mock_llm, mock_embeddings):
        with patch('app.models_api_client.ChatOpenAI', return_value=mock_llm), \
                patch('app.models_api_client.OpenAIEmbeddings', return_value=mock_embeddings):
            api_key = "test_key"
            client = ModelsApiClient(api_key, LlmModel.GPT_4o, EmbeddingModel.TEXT_EMB_3_small)

            assert client.llm == mock_llm
            assert client.embedding_model == mock_embeddings

    def test_create_response_for_llm_with_schema(self, mock_llm):
        with patch('app.models_api_client.ChatOpenAI', return_value=mock_llm):
            api_key = "test_key"
            client = ModelsApiClient(api_key)

            mock_prompt = MagicMock(spec=ChatPromptTemplate)
            mock_schema = {"type": "object"}

            response_data = {"content": "test content"}

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = response_data
            mock_prompt.__or__.return_value = mock_chain

            mock_structured_llm = MagicMock()
            mock_structured_llm.invoke.return_value = response_data
            mock_llm.with_structured_output.return_value = mock_structured_llm

            result = client.create_response_for_llm(TestDto, mock_prompt, mock_schema)

            assert result.content == "test content"
            mock_llm.with_structured_output.assert_called_once_with(
                schema=mock_schema, method="json_schema", strict=True
            )

    def test_create_response_for_llm_without_schema(self, mock_llm):
        with patch('app.models_api_client.ChatOpenAI', return_value=mock_llm):
            api_key = "test_key"
            client = ModelsApiClient(api_key)

            mock_prompt = MagicMock(spec=ChatPromptTemplate)
            mock_message = MagicMock()
            mock_message.content = "test content"

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_message
            mock_prompt.__or__.return_value = mock_chain

            result = client.create_response_for_llm(TestDto, mock_prompt)

            assert result.content == "test content"

    def test_get_embedding(self, mock_embeddings):
        with patch('app.models_api_client.OpenAIEmbeddings', return_value=mock_embeddings):
            api_key = "test_key"
            client = ModelsApiClient(api_key)

            test_embedding = [0.1, 0.2, 0.3]
            mock_embeddings.embed_query.return_value = test_embedding

            result = client.get_embedding("test text")

            assert result == test_embedding
            mock_embeddings.embed_query.assert_called_once_with("test text")

    def test_get_embedding_error(self, mock_embeddings, caplog):
        with patch('app.models_api_client.OpenAIEmbeddings', return_value=mock_embeddings):
            api_key = "test_key"
            client = ModelsApiClient(api_key)

            mock_embeddings.embed_query.side_effect = Exception("test error")

            result = client.get_embedding("test text")

            assert result == []
            assert "Ошибка при получении эмбеддингов: test error" in caplog.text

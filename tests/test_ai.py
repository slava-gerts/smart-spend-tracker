import pytest

from unittest.mock import patch, MagicMock

from apps.ai.parser import ExpenseParser
from apps.ai.schemas import ExpenseExtraction


@patch('apps.ai.parser.ChatPromptTemplate.from_messages')
@patch('langchain_groq.ChatGroq.with_structured_output')
def test_ai_parsing_mocked(mock_structured_llm, mock_prompt):
	mock_extraction = ExpenseExtraction(
		amount=500.0,
		currency="RSD",
		category="Food",
		description="pizza"
	)

	mock_prompt.return_value.__or__.return_value.invoke.return_value = mock_extraction

	parser = ExpenseParser()
	result = parser.parse_text("Yesterday I spent 500 RSD on pizza")

	assert result.amount == 500.0
	assert result.currency == "RSD"
	assert result.category.lower() in ["food", "other"]

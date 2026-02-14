import pytest

from unittest.mock import patch

from apps.ai.parser import ExpenseParser
from apps.ai.schemas import ExpenseList, ExpenseExtraction


@patch('apps.ai.parser.ChatPromptTemplate.from_messages')
@patch('langchain_groq.ChatGroq.with_structured_output')
def test_ai_parsing_mocked(mock_structured_llm, mock_prompt):
	mock_extraction = ExpenseList(expenses=[
		ExpenseExtraction(
			amount=500.0,
			currency="RSD",
			category="Food",
			description="pizza"
		),
		ExpenseExtraction(
			amount=200.0,
			currency="RSD",
			category="Transport",
			description="bus"
		)
	])

	mock_prompt.return_value.__or__.return_value.invoke.return_value = mock_extraction

	parser = ExpenseParser()
	result = parser.parse_text("Pizza 500 and bus 200")

	assert len(result.expenses) == 2
	assert result.expenses[0].amount == 500.0
	assert result.expenses[1].category == "Transport"

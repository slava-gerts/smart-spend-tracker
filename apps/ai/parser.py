from django.conf import settings

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from .schemas import ExpenseList


class ExpenseParser:
	def __init__(self):
		self.llm = ChatGroq(
			api_key=settings.GROQ_API_KEY,
			model_name="llama-3.3-70b-versatile",
			temperature=0
		)
		self.structured_llm = self.llm.with_structured_output(ExpenseList)

	def parse_text(self, text: str):
		prompt = ChatPromptTemplate.from_messages([
			("system", (
				"You are a professional financial assistant. "
				"Extract ALL expenses from the user's message as a structured list. "
				"Map currency names to ISO codes: "
				"'динары' or 'dinars' -> 'RSD', 'рубли' or 'rubles' -> 'RUB', 'доллары' or 'dollars' -> 'USD', 'евро' or 'euros' -> 'EUR'. "
				"If the currency is not specified, return null for the currency field. "
				"If the date is not specified, return null for the date field. "
				"Categories: Food, Transport, Rent, Shopping, Health, Utilities, Other."
			)),
			("human", "{input}")
		])

		chain = prompt | self.structured_llm
		return chain.invoke({"input": text})

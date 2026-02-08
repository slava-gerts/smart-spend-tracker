import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseExtraction(BaseModel):
	amount: float = Field(description="Amount of the expense")
	currency: Optional[str] = Field(default=None, description="Currency code (RSD, EUR, USD, RUB)")
	category: str = Field(description="Category of the expense (Food, Transport, etc.)")
	description: Optional[str] = Field(default=None, description="Description of the expense")
	date: Optional[datetime.date] = Field(default=None, description="Date of the expense (if provided, otherwise null)")

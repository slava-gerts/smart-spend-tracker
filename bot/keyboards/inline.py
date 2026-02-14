from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_transaction_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
	buttons = [
		[InlineKeyboardButton(text="🗑 Delete / Undo", callback_data=f"delete_tx:{transaction_id}")]
	]

	return InlineKeyboardMarkup(inline_keyboard=buttons)

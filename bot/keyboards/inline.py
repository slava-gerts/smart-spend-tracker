from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from apps.core.choices import CurrencyChoices


def get_transaction_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
	buttons = [
		[InlineKeyboardButton(text="🗑 Delete / Undo", callback_data=f"delete_tx:{transaction_id}")]
	]

	return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[InlineKeyboardButton(text="💱 Change Currency", callback_data="set_pref:currency")],
		[InlineKeyboardButton(text="🕒 Change Timezone", callback_data="set_pref:timezone")]
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_currency_keyboard() -> InlineKeyboardMarkup:
	buttons = []

	row = []
	for code, label in CurrencyChoices.choices:
		row.append(InlineKeyboardButton(text=f"{code}", callback_data=f"set_cur:{code}"))
		if len(row) == 2:
			buttons.append(row)
			row = []
	
	if row:
		buttons.append(row)

	buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="open_settings")])

	return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_timezone_keyboard() -> InlineKeyboardMarkup:
	zones = [
		('Europe/Belgrade', 'Belgrade 🇷🇸'),
		('Europe/Moscow', 'Moscow 🇷🇺'),
		('UTC', 'UTC 🌐'),
		('Europe/Berlin', 'Berlin 🇩🇪')
	]

	buttons = [[InlineKeyboardButton(text=label, callback_data=f"set_tz:{zone}")] for zone, label in zones]

	buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="open_settings")])

	return InlineKeyboardMarkup(inline_keyboard=buttons)

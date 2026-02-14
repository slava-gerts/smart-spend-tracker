from aiogram import Router, types, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from apps.users.models import Profile

from .keyboards.inline import get_settings_keyboard, get_currency_keyboard, get_timezone_keyboard


router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
	await message.answer(
		"⚙️ **Settings Menu**\nChoose what you want to change:",
		reply_markup=get_settings_keyboard(),
		parse_mode="Markdown"
	)


@router.callback_query(F.data == "open_settings")
async def back_to_settings(callback: types.CallbackQuery):
	await callback.message.edit_text(
		"⚙️ **Settings Menu**\nChoose what you want to change:",
		reply_markup=get_settings_keyboard(),
		parse_mode="Markdown"
	)


@router.callback_query(F.data == "set_pref:currency")
async def choose_currency(callback: types.CallbackQuery):
	await callback.message.edit_text(
		"💱 Choose your base currency:",
		reply_markup=get_currency_keyboard()
	)


@router.callback_query(F.data == "set_pref:timezone")
async def choose_timezone(callback: types.CallbackQuery):
	await callback.message.edit_text(
		"🕒 Choose your timezone:",
		reply_markup=get_timezone_keyboard()
	)


@router.callback_query(F.data.startswith("set_cur:"))
async def update_currency(callback: types.CallbackQuery):
	currency = callback.data.split(":")[1]
	profile = await sync_to_async(Profile.objects.get)(telegram_id=callback.from_user.id)
	profile.base_currency = currency
	await sync_to_async(profile.save)()
	await callback.message.edit_text(
		f"✅ Base currency updated to: **{currency}**",
		reply_markup=get_settings_keyboard(),
		parse_mode="Markdown"
	)


@router.callback_query(F.data.startswith("set_tz:"))
async def update_timezone(callback: types.CallbackQuery):
	tz_name = callback.data.split(":")[1]
	profile = await sync_to_async(Profile.objects.get)(telegram_id=callback.from_user.id)
	profile.timezone = tz_name
	await sync_to_async(profile.save)()
	await callback.message.edit_text(
		f"✅ Timezone updated to: **{tz_name}**",
		reply_markup=get_settings_keyboard(),
		parse_mode="Markdown"
	)

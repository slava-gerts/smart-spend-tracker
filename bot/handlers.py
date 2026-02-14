import os

from django.contrib.auth.models import User

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from apps.ai.stt import STTService
from apps.transactions.services import TransactionService
from apps.transactions.tasks import generate_monthly_report
from apps.users.models import Profile
from bot.keyboards.inline import get_transaction_keyboard

router = Router()

def get_or_create_user(message: types.Message) -> Profile:
	user, _ = User.objects.get_or_create(username=f"tg_{message.from_user.id}")
	profile, _ = Profile.objects.get_or_create(user=user, telegram_id=message.from_user.id)
	return profile

@router.message(Command("start"))
async def cmd_start(message: types.Message):
	await sync_to_async(get_or_create_user)(message)

	welcome_text = (
		"Welcome to Smart Spend Tracker! 💰\n\n"
		"Just send me a message like '500 dinars for lunch' or"
		"record a voice message, and I will track it for you." 
	)
	await message.answer(welcome_text)


@router.message(Command("report"))
async def cmd_report(message: types.Message):
	await message.answer("⏳ Generating your report... This might take a few seconds.")
	generate_monthly_report.delay(message.from_user.id)


@router.message(F.text)
async def handle_text_expense(message: types.Message):
	try:
		transactions = await sync_to_async(TransactionService.process_raw_message)(
			telegram_id=message.from_user.id,
			text=message.text
		)

		for tx in transactions:
			response = (
				f"✅ Saved!\n"
				f"Amount: {tx.amount} {tx.currency}\n"
				f"Category: {tx.category.name}\n"
				f"Description: {tx.description}"
			)
			await message.answer(response, reply_markup=get_transaction_keyboard(tx.id))
	except Exception as e:
		await message.answer(f"❌ Sorry, I couldn't parse that. Error: {str(e)}")


@router.message(F.voice)
async def handle_voice_expense(message: types.Message, bot: Bot):
	try:
		status_msg = await message.answer("🎧 Listening to your voice...")

		file_id = message.voice.file_id
		file = await bot.get_file(file_id)
		file_path = f"voice_{file_id}.ogg"
		await bot.download_file(file.file_path, file_path)

		stt = STTService()
		text = await sync_to_async(stt.transcribe)(file_path)

		if os.path.exists(file_path):
			os.remove(file_path)

		await status_msg.edit_text(f"📝 Transcribed: \"{text}\"\nProcessing...")

		transactions = await sync_to_async(TransactionService.process_raw_message)(
			telegram_id=message.from_user.id,
			text=text
		)

		for tx in transactions:
			await message.answer(
				f"✅ Voice Saved!\n"
				f"Amount: {tx.amount} {tx.currency}\n"
				f"Category: {tx.category.name}\n"
				f"Description: {tx.description}",
				reply_markup=get_transaction_keyboard(tx.id)
			)

		await status_msg.delete()
	except Exception as e:
		await message.answer(f"❌ Voice Error: {str(e)}")

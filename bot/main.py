import os
import sys
import asyncio
import logging

import django


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from django.conf import settings
from aiogram import Bot, Dispatcher

from bot.callbacks import router as callback_router
from bot.handlers import router
from bot.settings_handlers import router as settings_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def main():
	dp.include_router(settings_router)
	dp.include_router(router)
	dp.include_router(callback_router)
	
	logging.info("Starting bot...")
	await dp.start_polling(bot)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logging.info("Bot stopped!")
		

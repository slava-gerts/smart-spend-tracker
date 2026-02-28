from aiogram import Router, types, F
from asgiref.sync import sync_to_async

from apps.transactions.models import Transaction

router = Router()


def _delete_tx(transaction_id: int, telegram_id: int):
	try:
		tx = Transaction.objects.select_related('profile').get(id=transaction_id)
		if tx.profile.telegram_id != telegram_id:
			return 'forbidden'
		tx.delete()
		return True
	except Transaction.DoesNotExist:
		return False


@router.callback_query(F.data.startswith("delete_tx:"))
async def process_delete_transaction(callback: types.CallbackQuery):
	transaction_id = int(callback.data.split(":")[1])

	result = await sync_to_async(_delete_tx)(transaction_id, callback.from_user.id)

	if result is True:
		await callback.message.edit_text("✅ Transaction deleted")
	elif result == 'forbidden':
		await callback.answer("⛔ You can only delete your own transactions", show_alert=True)
	else:
		await callback.answer("❌ Transaction not found", show_alert=True)

from aiogram import Router, types, F
from asgiref.sync import sync_to_async

from apps.transactions.models import Transaction

router = Router()


def _delete_tx(transaction_id: int):
	try:
		tx = Transaction.objects.get(id=transaction_id)
		tx.delete()
		return True
	except Transaction.DoesNotExist:
		return False

@router.callback_query(F.data.startswith("delete_tx:"))
async def process_delete_transaction(callback: types.CallbackQuery):
	transaction_id = int(callback.data.split(":")[1])

	success = await sync_to_async(_delete_tx)(transaction_id)

	if success:
		await callback.message.edit_text("✅ Transaction deleted")
	else:
		await callback.answer("❌ Transaction not found", show_alert=True)

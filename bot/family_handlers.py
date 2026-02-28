from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from asgiref.sync import sync_to_async

from apps.users.models import Profile, Family

router = Router()


class FamilyState(StatesGroup):
	waiting_for_name = State()
	waiting_for_invite_code = State()


@router.message(Command("family"))
async def cmd_family(message: types.Message | types.CallbackQuery):
	user_id = message.from_user.id
	try:
		profile = await sync_to_async(Profile.objects.select_related('active_family').get)(telegram_id=user_id)
	except Profile.DoesNotExist:
		error_text = "❌ Profile not found. Please send /start first to register."
		if isinstance(message, types.Message):
			await message.answer(error_text)
		else:
			await message.message.answer(error_text)

		return

	text = "🏠 **Family Management**\n\n"

	if profile.active_family:
		text += f"Current mode: **Family** ({profile.active_family.name})\n"
		text += f"Share this Code to invite: `{profile.active_family.invite_code}`\n"
	else:
		text += "Current mode: **Personal** 👤\n"

	buttons = [
		[types.InlineKeyboardButton(text="➕ Create Family", callback_data="family_create")],
		[types.InlineKeyboardButton(text="🤝 Join by ID", callback_data="family_join")],
		[types.InlineKeyboardButton(text="📋 My Families", callback_data="family_list")]
	]

	if profile.active_family:
		buttons.append(
			[types.InlineKeyboardButton(text="👤 Switch to Personal", callback_data="family_switch:none")]
		)

	if isinstance(message, types.Message):
		await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
	elif isinstance(message, types.CallbackQuery):
		await message.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")


@router.callback_query(F.data == "family_create")
async def start_family_create(callback: types.CallbackQuery, state: FSMContext):
	await callback.message.edit_text("📝 Enter the name for your new family:")
	await state.set_state(FamilyState.waiting_for_name)


@router.callback_query(F.data == "family_join")
async def start_family_join(callback: types.CallbackQuery, state: FSMContext):
	await callback.message.edit_text("🔑 Enter the Family Code to join:")
	await state.set_state(FamilyState.waiting_for_invite_code)


@router.message(FamilyState.waiting_for_name)
async def process_family_name(message: types.Message, state: FSMContext):
	name = message.text
	profile = await sync_to_async(Profile.objects.get)(telegram_id=message.from_user.id)

	family = await sync_to_async(Family.objects.create)(name=name, owner=profile)
	await sync_to_async(family.members.add)(profile)

	profile.active_family = family
	await sync_to_async(profile.save)()

	await state.clear()
	await message.answer(f"✅ Family **{name}** created and set as active! (Code: `{family.invite_code}`)", parse_mode="Markdown")


@router.message(FamilyState.waiting_for_invite_code)
async def process_join_id(message: types.Message, state: FSMContext):
	code = message.text.strip().upper()
	try:
		family = await sync_to_async(Family.objects.get)(invite_code=code)
		profile = await sync_to_async(Profile.objects.get)(telegram_id=message.from_user.id)

		await sync_to_async(family.members.add)(profile)

		profile.active_family = family
		await sync_to_async(profile.save)()

		await state.clear()
		await message.answer(f"✅ Successfully joined **{family.name}**! mode: Family mode.", parse_mode="Markdown")
	except (ValueError, Family.DoesNotExist):
		await message.answer("❌ Invalid Family Code. Please try again.")


@router.callback_query(F.data == "family_list")
async def list_families(callback: types.CallbackQuery):
	profile = await sync_to_async(
		Profile.objects.select_related('active_family').prefetch_related('families').get
	)(telegram_id=callback.from_user.id)
	families = await sync_to_async(list)(profile.families.all())

	if not families:
		await callback.message.edit_text(
			"🤷‍♂️ You don't belong to any families yet.",
			reply_markup=types.InlineKeyboardMarkup(
				inline_keyboard=[
					[types.InlineKeyboardButton(text="⬅️ Back", callback_data="family_back")]
				]
			)
		)

		return

	text = "📋 **Your Families:**\n\n"
	buttons = []
	for f in families:
		status = "✅ (Active)" if profile.active_family == f else ""
		text += f"• **{f.name}** (Code: `{f.invite_code}`) {status}\n"

		buttons.append(
			[
				types.InlineKeyboardButton(text=f"Switch to {f.name}", callback_data=f"family_switch:{f.id}"),
				types.InlineKeyboardButton(text=f"🗑️", callback_data=f"family_confirm_delete:{f.id}")
			]
		)

	buttons.append(
		[types.InlineKeyboardButton(text="⬅️ Back", callback_data="family_back")]
	)

	await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")


@router.callback_query(F.data.startswith("family_switch:"))
async def switch_family(callback: types.CallbackQuery):
	data = callback.data.split(":")[1]

	profile = await sync_to_async(Profile.objects.get)(telegram_id=callback.from_user.id)

	if data == "none":
		profile.active_family = None
		mode = "Personal 👤"
	else:
		family = await sync_to_async(Family.objects.get)(id=int(data))
		profile.active_family = family
		mode = f"Family: {family.name} 🏠"

	await sync_to_async(profile.save)()
	await callback.answer(f"Switched to {mode}")

	await cmd_family(callback)


@router.callback_query(F.data.startswith("family_confirm_delete:"))
async def confirm_delete_family(callback: types.CallbackQuery):
	family_id = int(callback.data.split(":")[1])
	family = await sync_to_async(Family.objects.get)(id=family_id)

	text = f"🚨 **Are you sure you want to delete family '{family.name}'?**\n\n"
	text += "This action cannot be undone. All members will be switched to Personal mode."

	buttons = [
		[types.InlineKeyboardButton(text="❌ Yes, Delete", callback_data=f"family_delete_final:{family_id}")],
		[types.InlineKeyboardButton(text="⬅️ Cancel", callback_data="family_list")]
	]

	await callback.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")


@router.callback_query(F.data.startswith("family_delete_final:"))
async def delete_family_final(callback: types.CallbackQuery):
	family_id = int(callback.data.split(":")[1])
	try:
		family = await sync_to_async(Family.objects.select_related('owner').get)(id=family_id)

		if family.owner is None or family.owner.telegram_id != callback.from_user.id:
			await callback.answer("⛔ Only the family creator can delete it.", show_alert=True)
			return
			
		family_name = family.name
		await sync_to_async(family.delete)()
		await callback.answer(f"Family '{family_name}' deleted.")
	except Family.DoesNotExist:
		await callback.answer("Family already deleted.")

	await cmd_family(callback)


@router.callback_query(F.data == "family_back")
async def family_back(callback: types.CallbackQuery):
	await cmd_family(callback)

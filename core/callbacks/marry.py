from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.database import AsyncSessionLocal
from core.services import MarriageService, UserService
from core.exceptions import MarriageError

router = Router()


@router.callback_query(F.data.startswith("marry_accept:"))
async def accept_marry_callback(callback: CallbackQuery):
    """Обработка кнопки 'Согласен'."""
    group_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        user = callback.from_user
        _, membership = await UserService.get_user_with_membership(
            session, user.id, user.username, user.first_name, group_id
        )
        try:
            chat_text = await MarriageService.accept_marriage(session, membership)
            await callback.message.edit_text("💚 Ты согласился/лась! Поздравляем!")
            await callback.bot.send_message(chat_id=group_id, text=chat_text)
        except MarriageError as e:
            await callback.answer(str(e), show_alert=True)


@router.callback_query(F.data.startswith("marry_reject:"))
async def reject_marry_callback(callback: CallbackQuery):
    """Обработка кнопки 'Отказать'."""
    group_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        user = callback.from_user
        _, membership = await UserService.get_user_with_membership(
            session, user.id, user.username, user.first_name, group_id
        )
        try:
            chat_text = await MarriageService.reject_marriage(session, membership)
            await callback.message.edit_text("💔 Ты отказался/лась.")
            await callback.bot.send_message(chat_id=group_id, text=chat_text)
        except MarriageError as e:
            await callback.answer(str(e), show_alert=True)

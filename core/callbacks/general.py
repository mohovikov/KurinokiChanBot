from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.keyboards import inline
from core.messages.general import DM_RESPONSE, HELP_TEXT

router = Router()


@router.callback_query(F.data == "start")
async def callback_start(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        DM_RESPONSE, reply_markup=inline.commands_help_inline
    )


@router.callback_query(F.data == "help_commands")
async def callback_help_commands(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        HELP_TEXT, reply_markup=inline.back_to_mainpage_inline
    )

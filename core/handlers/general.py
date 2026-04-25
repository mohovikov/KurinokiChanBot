import logging
from aiogram import Router
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import (
    CommandStart,
    Command,
    ChatMemberUpdatedFilter,
    IS_NOT_MEMBER,
    IS_MEMBER,
)

from core.messages.general import DM_RESPONSE, HELP_TEXT, WELCOME_TEXT
from core.keyboards import inline

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(DM_RESPONSE, reply_markup=inline.commands_help_inline)


@router.message(Command("help"))
async def help_me(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=inline.back_to_mainpage_inline)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER)
)
async def on_bot_added_to_group(event: ChatMemberUpdated) -> None:
    """Handler, когда бота добавляют в общий чат"""

    logger.debug(f"Бот добавлен в чат: {event.chat.title} (ID: {event.chat.id})")
    await event.bot.send_message(
        chat_id=event.chat.id, text=WELCOME_TEXT, parse_mode="HTML"
    )

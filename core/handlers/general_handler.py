import logging
from aiogram import Router, Bot
from aiogram.types import Message, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram.filters import (
    CommandStart,
    Command,
    ChatMemberUpdatedFilter,
    IS_NOT_MEMBER,
    IS_MEMBER,
)

from core.messages.general import DM_RESPONSE, HELP_TEXT, WELCOME_TEXT
from core.keyboards import inline
from core.filters import ChatTypeFilter
from core.services import UserService

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
    await event.bot.send_message(chat_id=event.chat.id, text=WELCOME_TEXT)


@router.message(
    ChatTypeFilter(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP]),
    lambda msg: msg.new_chat_members is not None,
)
async def on_user_join(message: Message, bot: Bot):
    """Приветствует новых участников."""
    for new_member in message.new_chat_members:
        # Не приветствуем бота
        if new_member.is_bot:
            continue

        user_name = new_member.mention_html()
        await UserService.greet_new_member(
            bot=bot,
            chat_id=message.chat.id,
            user_name=user_name,
            user_id=new_member.id,
        )
        logger.info(
            f"👋 Приветствуем нового участника: @{new_member.username} в чате {message.chat.id}"
        )


@router.message(
    ChatTypeFilter(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP]),
    lambda msg: msg.left_chat_member is not None,
)
async def on_user_leave(message: Message):
    """Обрабатывает выход или удаление участника из чата."""
    left_user = message.left_chat_member

    # Не трогаем ботов
    if left_user.is_bot:
        return

    await UserService.remove_membership(
        user_id=left_user.id,
        group_id=message.chat.id,
    )

    logger.info(f"👋 Участник покинул чат: @{left_user.username} (ID: {left_user.id})")

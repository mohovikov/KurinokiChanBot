import logging
from aiogram import Router
from aiogram.types import Message

from core.database import AsyncSessionLocal
from core.exceptions import MarriageError
from core.keyboards.inline import get_proposal_keyboard
from core.filters import VoiceFilter
from core.messages.keywords import MARRY_KEYWORDS, DIVORCE_KEYWORDS
from core.services import MarriageService, UserService

router = Router()
logger = logging.getLogger(__name__)


@router.message(VoiceFilter(*MARRY_KEYWORDS))
async def marry_command(message: Message, query: str):
    """Предложение руки и сердца: /брак @username."""
    target_username = None

    # Ищем @username в entities
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                target_username = entity.user.username
                break
            elif entity.type == "mention":
                target_username = message.text[
                    entity.offset + 1 : entity.offset + entity.length
                ]
                break

    # Если entities нет — берём второй аргумент
    if not target_username:
        args = message.text.split()
        if len(args) > 1:
            target_username = args[1].lstrip("@")

    if not target_username:
        await message.reply("❓ Кого желаете взять в мужья/жёны? Укажите @username!")
        return

    async with AsyncSessionLocal() as session:
        try:
            initiator = message.from_user
            _, init_membership = await UserService.get_user_with_membership(
                session,
                initiator.id,
                initiator.username,
                initiator.first_name,
                message.chat.id,
            )
            target_membership = await MarriageService.get_membership_by_username(
                session, message.chat.id, target_username
            )

            if not target_membership:
                await message.reply(
                    "❓ Я не знаю такого человека в этом чате. Пусть напишет что-нибудь!"
                )
                return

            await MarriageService.propose_marriage(
                session, init_membership, target_membership
            )

            # Сообщение в чат
            await message.reply(
                f"💍 <b>{initiator.first_name}</b> предложил(а) "
                f"<b>{target_membership.user.first_name}</b> руку и сердце!\n\n"
                f"⏳ Ждём ответа в ЛС...",
                parse_mode="HTML",
            )

            # Сообщение в ЛС
            try:
                await message.bot.send_message(
                    chat_id=target_membership.user.telegram_id,
                    text=(
                        f"💍 <b>{initiator.first_name}</b> хочет на тебе жениться "
                        f"в чате <b>{message.chat.title}</b>!\n\nТвой ответ?"
                    ),
                    reply_markup=get_proposal_keyboard(group_id=message.chat.id),
                )
            except Exception as e:
                logger.warning(f"Не смог отправить ЛС: {e}")
                await message.reply(
                    "⚠️ Не смог отправить предложение в ЛС. Пусть пользователь напишет боту в личку!"
                )

        except MarriageError as e:
            await message.reply(str(e))


@router.message(VoiceFilter(*DIVORCE_KEYWORDS))
async def divorce_command(message: Message, query: str):
    """Развод: /развод."""
    async with AsyncSessionLocal() as session:
        user = message.from_user
        _, membership = await UserService.get_user_with_membership(
            session, user.id, user.username, user.first_name, message.chat.id
        )
        try:
            chat_text = await MarriageService.divorce(session, membership)
            await message.reply(chat_text)
        except MarriageError as e:
            await message.reply(str(e))

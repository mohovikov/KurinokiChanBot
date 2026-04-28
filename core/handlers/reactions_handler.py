# core/handlers/reactions.py
import random
from aiogram import Router, types
from aiogram.enums import ChatType

from core.filters import ChatTypeFilter, VoiceFilter
from core.messages.reactions import REACTIONS
from core.messages.keywords import (
    PROFILE_KEYWORDS,
    MARRY_KEYWORDS,
    DIVORCE_KEYWORDS,
    HUG_KEYWORDS,
)

router = Router()

GROUP_FILTER = ChatTypeFilter(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
ALL_COMMAND_KEYWORDS = (
    PROFILE_KEYWORDS + MARRY_KEYWORDS + DIVORCE_KEYWORDS + HUG_KEYWORDS
)


def find_reaction(text: str) -> str | None:
    """Ищет подходящую реакцию по тексту сообщения."""
    text_lower = text.lower()
    for keywords, responses in REACTIONS:
        if any(kw in text_lower for kw in keywords):
            return random.choice(responses)
    return None


def is_command(query: str) -> bool:
    """Проверяет, не является ли запрос командой (профиль, брак и т.д.)."""
    return any(kw in query.lower() for kw in ALL_COMMAND_KEYWORDS)


@router.message(VoiceFilter())
async def reaction_handler(message: types.Message, query: str):
    """Реагирует на обычные фразы в чате."""
    if is_command(query):
        return

    reaction = find_reaction(query)
    if reaction:
        await message.reply(reaction)

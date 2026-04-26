import logging
from aiogram import Router
from aiogram.types import Message

from core.filters import VoiceFilter
from core.messages.general import HELP_TEXT_BY_VOICE_FALLBACK
from core.messages.keywords import (
    HUG_KEYWORDS,
    PROFILE_KEYWORDS,
    MARRY_KEYWORDS,
    DIVORCE_KEYWORDS,
)


router = Router()
logger = logging.getLogger(__name__)


@router.message(VoiceFilter(*PROFILE_KEYWORDS))  # ← просто звёздочка перед списком
async def voice_profile(message: Message, query: str):
    await message.reply("🌰 Профиль в разработке!")


@router.message(VoiceFilter(*MARRY_KEYWORDS))
async def voice_marry(message: Message, query: str):
    await message.reply("💍 Брачная логика в разработке!")


@router.message(VoiceFilter(*DIVORCE_KEYWORDS))
async def voice_divorce(message: Message, query: str):
    await message.reply("💔 Разводная логика в разработке!")


@router.message(VoiceFilter(*HUG_KEYWORDS))
async def voice_hug(message: Message, query: str):
    await message.reply("🤗 Обнимашки в разработке!")


@router.message(VoiceFilter())  # ← без аргументов = ловит ВСЁ
async def voice_fallback(message: Message, query: str):
    await message.reply(HELP_TEXT_BY_VOICE_FALLBACK)

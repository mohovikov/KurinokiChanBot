import logging
from aiogram import Router
from aiogram.types import Message

from core.filters import VoiceFilter
from core.messages.keywords import PROFILE_KEYWORDS
from core.services import UserService

router = Router()
logger = logging.getLogger(__name__)


@router.message(VoiceFilter(*PROFILE_KEYWORDS))
async def voice_profile(message: Message, db_user, membership, query: str):
    await UserService.get_user_profile(message, db_user, membership)

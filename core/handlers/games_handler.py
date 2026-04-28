import logging
from aiogram import Router, types

from core.filters import VoiceFilter
from core.services import GameService
from core.messages.games import (
    DICE_COMMENTS,
    DICE_KEYWORDS,
    DART_COMMENTS,
    DART_KEYWORDS,
    CASINO_COMMENTS,
    CASINO_KEYWORDS,
    BASKETBALL_COMMENTS,
    BASKETBALL_KEYWORDS,
    FOOTBALL_COMMENTS,
    FOOTBALL_KEYWORDS,
    BOWLING_COMMENTS,
    BOWLING_KEYWORDS,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(VoiceFilter(*DICE_KEYWORDS))
async def dice_voice(message: types.Message, query: str):
    """🎲 Игральная кость."""
    await GameService.send_game(message, "🎲", DICE_COMMENTS)


@router.message(VoiceFilter(*DART_KEYWORDS))
async def dart_voice(message: types.Message, query: str):
    """🎯 Дартс."""
    await GameService.send_game(message, "🎯", DART_COMMENTS)


@router.message(VoiceFilter(*CASINO_KEYWORDS))
async def casino_voice(message: types.Message, query: str):
    """🎰 Слот-машина."""
    await GameService.send_game(message, "🎰", CASINO_COMMENTS)


@router.message(VoiceFilter(*BASKETBALL_KEYWORDS))
async def basketball_voice(message: types.Message, query: str):
    """🏀 Баскетбол."""
    await GameService.send_game(message, "🏀", BASKETBALL_COMMENTS)


@router.message(VoiceFilter(*FOOTBALL_KEYWORDS))
async def football_voice(message: types.Message, query: str):
    """⚽ Футбол."""
    await GameService.send_game(message, "⚽", FOOTBALL_COMMENTS)


@router.message(VoiceFilter(*BOWLING_KEYWORDS))
async def bowling_voice(message: types.Message, query: str):
    """🎳 Боулинг."""
    await GameService.send_game(message, "🎳", BOWLING_COMMENTS)

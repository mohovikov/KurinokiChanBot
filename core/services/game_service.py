import asyncio
import logging
from aiogram.types import Message

from core.messages.games import GAME_TIMINGS

logger = logging.getLogger(__name__)


class GameService:
    @staticmethod
    async def send_game(message: Message, emoji: str, comments: dict[int, str]) -> None:
        """Отправляет игру и ждёт результат от Telegram."""
        sent = await message.answer_dice(emoji=emoji)
        value = sent.dice.value

        delay = GAME_TIMINGS.get(emoji, 4.0)
        await asyncio.sleep(delay)

        comment = comments.get(value, f"🌰 Результат: {value}! Каштанчик засчитал!")
        await message.reply(comment)

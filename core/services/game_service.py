import asyncio
import logging
from aiogram.types import Message, ReactionTypeEmoji

from core.messages.games import GAME_TIMINGS, GAME_MAX_VALUES, MAX_RESULT_REACTIONS

logger = logging.getLogger(__name__)


class GameService:
    @staticmethod
    async def send_game(message: Message, emoji: str, comments: dict[int, str]) -> None:
        """Отправляет игру и ждёт результат от Telegram."""
        # sent = await message.answer_dice(emoji=emoji)
        sent = await message.reply_dice(emoji=emoji)
        value = sent.dice.value
        logger.debug(f"Game: {emoji}, value: {value}")

        delay = GAME_TIMINGS.get(emoji, 4.0)
        await asyncio.sleep(delay)

        comment = comments.get(value, f"🌰 Результат: {value}! Каштанчик засчитал!")

        max_value = GAME_MAX_VALUES.get(emoji)
        if value == max_value:
            reactions = MAX_RESULT_REACTIONS.get(emoji, ["🔥", "🌟"])
            message = await message.reply(
                f"{comment}\n\n"
                f"🌟 <b>МАКСИМАЛЬНЫЙ РЕЗУЛЬТАТ!</b> Каштанчик в экстазе! 🌰✨",
            )

            try:
                for reaction in reactions:
                    await sent.react([ReactionTypeEmoji(emoji=reaction)])
                    await message.react([ReactionTypeEmoji(emoji=reaction)])
            except Exception:
                pass
        else:
            await message.reply(comment)

from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.enums import ChatType

from core.constants import BOT_NAMES


class VoiceFilter(Filter):
    """
    Универсальный фильтр для голосовых команд

    Args:
        *keywords (str): ключевые слова (пусто = fallback)
        groups (bool – Default True): True – группы, False – личка, None – везде

    Examples:
        - Только в группах – :obj:`VoiceFilter("профиль", groups=True)`
        - Fallback в группах – :obj:`VoiceFilter(groups=True)`
        - Только в личке – :obj:`VoiceFilter("старт", groups=False)`
        - Вообще везде – :obj:`VoiceFilter()`
    """

    def __init__(self, *keywords: str, groups: bool | None = True) -> None:
        self.keywords = keywords
        self.groups = groups

    async def __call__(self, message: Message) -> dict | bool:
        if self.groups is not None:
            if self.groups and message.chat.type not in [
                ChatType.GROUP,
                ChatType.SUPERGROUP,
            ]:
                return False
            if not self.groups and message.chat.type != ChatType.PRIVATE:
                return False
        if not message.text:
            return False

        text = message.text.strip().lower()

        for name in BOT_NAMES:
            if text.startswith(name):
                query = text[len(name) :].strip().lstrip(",.!?")

                # Пропускаем, если не указаны ключевые слова
                if not self.keywords:
                    return {"query": query}

                # Проверка на ключевые слова
                if any(kw in query for kw in self.keywords):
                    return {"query": query}

        return False

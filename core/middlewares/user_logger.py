# core/middlewares/user_logger.py
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.enums import ChatType
from core.database import AsyncSessionLocal
from core.services import UserService

logger = logging.getLogger(__name__)


class UserLoggerMiddleware(BaseMiddleware):
    """Записывает пользователя в БД при каждом сообщении в группе."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        # Только группы
        if event.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return await handler(event, data)

        user = event.from_user
        if user is None:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            try:
                db_user, membership = await UserService.get_user_with_membership(
                    session=session,
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    group_id=event.chat.id,
                )
                data["db_user"] = db_user
                data["membership"] = membership
            except Exception as e:
                logger.error(f"Ошибка в middleware: {e}")

        return await handler(event, data)

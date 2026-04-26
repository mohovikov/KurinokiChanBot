import logging
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.database.models import User, Membership

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def sync_bot_user(bot: Bot) -> None:
        bot_user = await bot.get_me()

        async with AsyncSessionLocal() as session:
            db_bot = await session.get(User, 99)

            if db_bot:
                updated = False

                if db_bot.telegram_id != bot_user.id:
                    db_bot.telegram_id = bot_user.id
                    updated = True

                if db_bot.username != bot_user.username:
                    db_bot.username = bot_user.username
                    updated = True

                if db_bot.first_name != bot_user.first_name:
                    db_bot.first_name = bot_user.first_name
                    updated = True

                if updated:
                    await session.commit()
                    logger.info(
                        f"🌰 Бот обновлён: @{bot_user.username} (ID: {bot_user.id})"
                    )
                else:
                    logger.info(f"🌰 Бот уже актуален: @{bot_user.username}")

    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: str | None,
        first_name: str,
    ) -> User:
        """Получает существующего пользователя или создаёт нового."""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id, username=username, first_name=first_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"✨ Новый пользователь: @{username} (ID: {telegram_id})")
        else:
            updated = False
            if user.username != username:
                user.username = username
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if updated:
                await session.commit()
                await session.refresh(user)
                logger.debug(f"🔄 Обновлён: @{username}")

        return user

    @staticmethod
    async def get_or_create_membership(
        session: AsyncSession,
        user: User,
        group_id: int,
    ) -> Membership:
        """Получает или создаёт Membership пользователя в группе."""
        result = await session.execute(
            select(Membership)
            .where(Membership.user_id == user.id, Membership.group_id == group_id)
            .options(selectinload(Membership.user))
        )
        membership = result.scalar_one_or_none()

        if membership is None:
            membership = Membership(user_id=user.id, group_id=group_id)
            session.add(membership)
            await session.commit()
            await session.refresh(membership)
            # Перезагружаем с user'ом
            result = await session.execute(
                select(Membership)
                .where(Membership.id == membership.id)
                .options(selectinload(Membership.user))
            )
            membership = result.scalar_one()
            logger.info(f"📝 Новый membership: @{user.username} в чате {group_id}")

        return membership

    @staticmethod
    async def get_user_with_membership(
        session: AsyncSession,
        telegram_id: int,
        username: str | None,
        first_name: str,
        group_id: int,
    ) -> tuple[User, Membership]:
        """Получает (или создаёт) User и Membership одним вызовом."""
        user = await UserService.get_or_create_user(
            session, telegram_id, username, first_name
        )
        membership = await UserService.get_or_create_membership(session, user, group_id)
        return user, membership

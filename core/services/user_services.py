import logging
from datetime import datetime
from random import choice
from aiogram import Bot
from aiogram.types import Message
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import CREATOR_TELEGRAM_ID
from core.database import AsyncSessionLocal
from core.database.models import User, Membership
from core.messages.general import PROFILE, WELCOME_MESSAGES

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

            # Моя хотелка
            if user.telegram_id == CREATOR_TELEGRAM_ID:
                bot_membership_result = await session.execute(
                    select(Membership).where(
                        Membership.user_id == 99, Membership.group_id == group_id
                    )
                )
                bot_membership = bot_membership_result.scalar_one_or_none()

                if bot_membership is None:
                    bot_user_result = await session.execute(
                        select(User).where(User.id == 99)
                    )
                    bot_user = bot_user_result.scalar_one()
                    bot_membership = Membership(user_id=bot_user.id, group_id=group_id)
                    session.add(bot_membership)
                    await session.flush()

                # Заключаем брак
                now = datetime.utcnow()
                membership.married_to_id = 99
                membership.married_at = now
                bot_membership.married_to_id = user.id
                bot_membership.married_at = now

                await session.commit()
                await session.refresh(membership)
                logger.info(
                    f"💍 Создатель @{user.username} автоматически женат на Каштанчике!"
                )

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

    @staticmethod
    async def get_user_profile(
        message: Message, user: User, membership: Membership
    ) -> None:
        """Показывает профиль пользователя."""

        async with AsyncSessionLocal() as session:
            stmt = (
                select(Membership)
                .where(Membership.id == membership.id)
                .options(
                    selectinload(Membership.married_to), selectinload(Membership.user)
                )
            )
            result = await session.execute(stmt)
            membership = result.scalar_one()

            # Брачный статус
            if membership.married_to:
                marriage_status = (
                    f"💍 В браке с <b>{membership.married_to.first_name}</b>"
                )
            else:
                marriage_status = "💔 Свободен(на)"

            await message.reply(
                PROFILE.format(
                    username=user.first_name if user.first_name else user.username,
                    hugs_given=membership.hugs_given,
                    warns_count=membership.warns_count,
                    marriage_score=membership.marriage_score,
                    marriage_status=marriage_status,
                    joined_at=membership.joined_at.strftime("%d.%m.%Y"),
                )
            )

    @staticmethod
    async def greet_new_member(bot: Bot, chat_id: int, user_name: str, user_id: int):
        """Отправляет приветствие новому участнику."""
        message = choice(WELCOME_MESSAGES).format(user=user_name)
        await bot.send_message(chat_id=chat_id, text=message)

    @staticmethod
    async def remove_membership(user_id: int, group_id: int) -> None:
        """Удаляет Membership пользователя в группе"""
        async with AsyncSessionLocal() as session:
            user_result = await session.execute(
                select(User.id).where(User.telegram_id == user_id)
            )
            internal_user_id = user_result.scalar_one_or_none()

            if internal_user_id is None:
                logger.warning(f"Пользователь с telegram_id={user_id} не найден в БД")
                return

            result = await session.execute(
                delete(Membership).where(
                    Membership.user_id == internal_user_id,
                    Membership.group_id == group_id,
                )
            )
            await session.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(
                    f"🗑️ Membership удалён: user_id={user_id}, group_id={group_id}"
                )

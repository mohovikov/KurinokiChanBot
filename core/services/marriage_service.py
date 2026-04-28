import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import User, Membership
from core.exceptions import MarriageError

logger = logging.getLogger(__name__)


class MarriageService:
    @staticmethod
    async def get_membership_by_username(
        session: AsyncSession, group_id: int, target_username: str
    ) -> Membership | None:
        """Ищет Membership пользователя по @username в конкретной группе."""
        clean_username = target_username.lstrip("@")
        stmt = (
            select(Membership)
            .join(User, Membership.user_id == User.id)
            .where(User.username == clean_username, Membership.group_id == group_id)
            .options(selectinload(Membership.user))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def propose_marriage(
        session: AsyncSession,
        proposer: Membership,
        target: Membership,
    ) -> None:
        """Создаёт предложение руки и сердца."""
        # Приаттачиваем к сессии и загружаем user'ов
        proposer = await session.merge(proposer)
        target = await session.merge(target)

        stmt = (
            select(Membership)
            .where(Membership.id == proposer.id)
            .options(selectinload(Membership.user))
        )
        proposer = (await session.execute(stmt)).scalar_one()

        stmt = (
            select(Membership)
            .where(Membership.id == target.id)
            .options(selectinload(Membership.user))
        )
        target = (await session.execute(stmt)).scalar_one()

        # Проверки
        if proposer.married_to_id:
            raise MarriageError("🌰 Ты уже состоишь в браке! Сначала разведись.")
        if target.married_to_id:
            raise MarriageError("🌰 Твой избранник уже занят.")
        if proposer.user_id == target.user_id:
            raise MarriageError("🌰 Нельзя жениться на себе.")
        if proposer.pending_proposal_to_id:
            raise MarriageError("🌰 Ты уже сделал предложение! Дождись ответа.")
        if target.pending_proposal_to_id:
            raise MarriageError(
                "🌰 Этот человек сейчас решает судьбу другого предложения. Подожди."
            )

        proposer.pending_proposal_to_id = target.user_id
        await session.commit()
        logger.info(
            f"💍 Предложение: {proposer.user_id} -> {target.user_id} в чате {proposer.group_id}"
        )

    @staticmethod
    async def accept_marriage(
        session: AsyncSession,
        acceptor: Membership,
    ) -> str:
        """Принимает предложение. Возвращает текст для чата."""
        acceptor = await session.merge(acceptor)
        stmt = (
            select(Membership)
            .where(Membership.id == acceptor.id)
            .options(selectinload(Membership.user))
        )
        acceptor = (await session.execute(stmt)).scalar_one()

        # Ищем, кто сделал предложение этому человеку
        stmt = (
            select(Membership)
            .where(
                Membership.pending_proposal_to_id == acceptor.user_id,
                Membership.group_id == acceptor.group_id,
            )
            .options(selectinload(Membership.user))
        )
        proposer = (await session.execute(stmt)).scalar_one_or_none()

        if not proposer:
            raise MarriageError("❓ На тебя нет активного предложения.")

        now = datetime.utcnow()
        proposer.married_to_id = acceptor.user_id
        proposer.married_at = now
        proposer.pending_proposal_to_id = None

        acceptor.married_to_id = proposer.user_id
        acceptor.married_at = now

        await session.commit()
        logger.info(
            f"🎉 Брак: {proposer.user_id} + {acceptor.user_id} в чате {proposer.group_id}"
        )

        return (
            f"🎉 <b>{acceptor.user.first_name}</b> согласился/лась! "
            f"<b>{proposer.user.first_name}</b> и <b>{acceptor.user.first_name}</b> "
            f"теперь муж и жена! Горько! 🍯"
        )

    @staticmethod
    async def reject_marriage(
        session: AsyncSession,
        rejector: Membership,
    ) -> str:
        """Отклоняет предложение. Возвращает текст для чата."""
        rejector = await session.merge(rejector)
        stmt = (
            select(Membership)
            .where(Membership.id == rejector.id)
            .options(selectinload(Membership.user))
        )
        rejector = (await session.execute(stmt)).scalar_one()

        stmt = (
            select(Membership)
            .where(
                Membership.pending_proposal_to_id == rejector.user_id,
                Membership.group_id == rejector.group_id,
            )
            .options(selectinload(Membership.user))
        )
        proposer = (await session.execute(stmt)).scalar_one_or_none()

        if not proposer:
            raise MarriageError("❓ На тебя нет активного предложения.")

        proposer_name = proposer.user.first_name
        proposer.pending_proposal_to_id = None
        await session.commit()
        logger.info(f"💔 Отказ: {rejector.user_id} отказал {proposer.user_id}")

        return (
            f"💔 <b>{rejector.user.first_name}</b> отказался/лась. "
            f"<b>{proposer_name}</b>, не грусти! Каштанчик с тобой 🌰"
        )

    @staticmethod
    async def divorce(
        session: AsyncSession,
        initiator: Membership,
    ) -> str:
        """Развод. Возвращает текст для чата."""
        initiator = await session.merge(initiator)
        stmt = (
            select(Membership)
            .where(Membership.id == initiator.id)
            .options(selectinload(Membership.user))
        )
        initiator = (await session.execute(stmt)).scalar_one()

        if not initiator.married_to_id:
            raise MarriageError("🌰 Ты не состоишь в браке.")

        # Ищем супруга
        stmt = (
            select(Membership)
            .where(
                Membership.user_id == initiator.married_to_id,
                Membership.group_id == initiator.group_id,
            )
            .options(selectinload(Membership.user))
        )
        spouse = (await session.execute(stmt)).scalar_one_or_none()

        ex_name = spouse.user.first_name if spouse else "Неизвестный"

        if spouse:
            spouse.married_to_id = None
            spouse.married_at = None

        initiator.married_to_id = None
        initiator.married_at = None
        await session.commit()
        logger.info(
            f"💔 Развод: {initiator.user_id} + {spouse.user_id if spouse else '?'}"
        )

        return f"💔 <b>{initiator.user.first_name}</b> и <b>{ex_name}</b> официально разведены. Каштан грустит. 🌰😢"

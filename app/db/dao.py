from datetime import datetime, UTC, timedelta
from typing import Optional, List, Dict

from loguru import logger
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import BaseDAO
from app.db.models import User, Team, Hackathon, Member, Invite


class UserDAO(BaseDAO[User]):
    model = User

    async def get_user_id(cls, session: AsyncSession, telegram_id: int) -> int | None:
        """
        Получает ID пользователя по его Telegram ID.
        """
        logger.info(f"Получение user_id по telegram_id: {telegram_id}")
        try:
            query = select(cls.model.id).filter_by(telegram_id=telegram_id)
            result = await session.execute(query)
            user_id = result.scalar_one_or_none()
            if user_id:
                logger.info(f"Найден user_id: {user_id} для telegram_id: {telegram_id}")
            else:
                logger.info(f"User с telegram_id: {telegram_id} не найден.")
            return user_id
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении user_id по telegram_id {telegram_id}: {e}")
            raise


class TeamDAO(BaseDAO[Team]):
    model = Team

    @classmethod
    async def find_all_by_hackathon_id(cls, session: AsyncSession, hackathon_id: int) -> List[Team]:
        """
        Получает список всех команд, принадлежащих к определенному хакатону.
        """
        logger.info(f"Поиск всех команд для hackathon_id: {hackathon_id}")
        try:
            query = select(cls.model).where(cls.model.hackathon_id == hackathon_id)
            result = await session.execute(query)
            teams = result.scalars().all()
            logger.info(f"Найдено {len(teams)} команд для hackathon_id: {hackathon_id}")
            return teams
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске команд для hackathon_id {hackathon_id}: {e}")
            raise

    @classmethod
    async def find_team_with_members_by_user_id(cls, session: AsyncSession, user_id: int) -> Team | None:
        """
        Находит команду (и ее участников), в которой состоит пользователь с указанным ID.
        """
        try:
            query = (
                select(Team)
                .join(Member, Team.id == Member.team_id)
                .where(Member.user_id == user_id)
            )

            result = await session.execute(query)
            team = result.scalar_one_or_none()

            if team:
                logger.info(f"Команда найдена для user ID {user_id}: {team.name}")
            else:
                logger.info(f"Команда не найдена для user ID {user_id}")

            return team

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске команды с участниками для user ID {user_id}: {e}")
            raise


class HackathonDAO(BaseDAO[Hackathon]):
    model = Hackathon


class MemberDAO(BaseDAO[Member]):
    model = Member

    @classmethod
    async def find_all_by_team_id(cls, team_id: int, session: AsyncSession) -> List[Member]:
        query = select(cls.model).where(cls.model.team_id == team_id)
        result = await session.execute(query)
        return result.scalars().all()


class InviteDAO(BaseDAO[Invite]):
    model = Invite
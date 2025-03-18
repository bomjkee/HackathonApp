from typing import List
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.schemas import HackathonIDModel
from app.db.base import BaseDAO
from app.db.models import User, Team, Hackathon, Member, Invite


class UserDAO(BaseDAO[User]):
    model = User

    async def get_user_id(self, telegram_id: int) -> int | None:
        """
        Получает ID пользователя по его Telegram ID.
        """
        logger.info(f"Получение user_id по telegram_id: {telegram_id}")
        try:
            query = select(self.model.id).filter_by(telegram_id=telegram_id)
            result = await self._session.execute(query)
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

    async def find_all_teams_by_user_id(self, user_id: int):
        """
        Находит команду (и ее участников), в которой состоит пользователь с указанным ID.
        """
        try:
            query = (
                select(self.model)
                .join(Member, self.model.id == Member.team_id)
                .where(Member.user_id == user_id)
            )

            result = await self._session.execute(query)
            teams = result.scalars().all()

            if len(teams) > 0:
                logger.info(f"Команды найдены для пользователя c ID {user_id}: {teams}")
            else:
                logger.info(f"Команды не найдены для пользователя user ID {user_id}")

            return teams

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске команды с участниками для user ID {user_id}: {e}")
            raise


class HackathonDAO(BaseDAO[Hackathon]):
    model = Hackathon


class MemberDAO(BaseDAO[Member]):
    model = Member

    async def find_existing_member(self, user_id: int, hackathon_id: int):
        try:
            logger.info(f"Поиск существующего участника с user_id: {user_id} и hackathon_id: {hackathon_id}")
            query = (
                select(self.model)
                .join(Team, self.model.team_id == Team.id)
                .where(self.model.user_id == user_id, Team.hackathon_id == hackathon_id)
            )

            result = await self._session.execute(query)
            member = result.scalars().first()

            if member:
                logger.info(f"Найден участник с user_id: {user_id} и hackathon_id: {hackathon_id}")
            else:
                logger.info(f"Участник с user_id: {user_id} и hackathon_id: {hackathon_id} не найден")
            return member
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске участника с user_id {user_id} и hackathon_id {hackathon_id}: {e}")
            raise


    async def find_members_by_hackathon(self, filters: HackathonIDModel):
        try:
            hackathon_id = filters.model_dump(exclude_unset=True)
            logger.info(f"Поиск существующих участников для hackathon_id: {hackathon_id}")
            query = (
                select(self.model)
                .join(Team, self.model.team_id == Team.id)
                .where(Team.hackathon_id == hackathon_id)
            )

            result = await self._session.execute(query)
            members = result.scalars().all()

            if members:
                logger.info(f"Найдены участники для hackathon_id: {hackathon_id}")
            else:
                logger.info(f"Участники для hackathon_id: {hackathon_id} не найдены")
            return members
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске участника для hackathon_id {hackathon_id}: {e}")
            raise


class InviteDAO(BaseDAO[Invite]):
    model = Invite

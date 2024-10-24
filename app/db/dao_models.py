from app.db.models import User, Team, Hackathon, Member
from app.db.dao.base import BaseDAO

class UserDAO(BaseDAO):
    model = User


class TeamDAO(BaseDAO):
    model = Team


class HackathonDAO(BaseDAO):
    model = Hackathon


class MemberDAO(BaseDAO):
    model = Member

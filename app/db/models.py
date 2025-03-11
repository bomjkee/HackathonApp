from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, ForeignKey, String
from datetime import datetime
from typing import List
from app.db.database import Base



class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]

    photo_url: Mapped[str | None]
    auth_date: Mapped[datetime | None]


    full_name: Mapped[str | None]
    is_mirea_student: Mapped[bool | None]
    group: Mapped[str | None]


    members: Mapped[List["Member"]] = relationship("Member", back_populates="user")
    invites: Mapped[List["Invite"]] = relationship("Invite", back_populates="user")


class Team(Base):
    name: Mapped[str]
    is_open: Mapped[bool]
    description: Mapped[str | None]
    hackathon_id: Mapped[int] = mapped_column(Integer, ForeignKey("hackathons.id", ondelete="CASCADE"))

    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="teams")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="team")
    invites: Mapped[List["Invite"]] = relationship("Invite", back_populates="team")


class Hackathon(Base):
    name: Mapped[str]
    start_description: Mapped[str]
    description: Mapped[str]
    max_members: Mapped[int]
    start_date: Mapped[datetime | None]
    end_date: Mapped[datetime | None]

    teams: Mapped[List["Team"]] = relationship("Team", back_populates="hackathon")


class Member(Base):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    tg_name: Mapped[str]
    role: Mapped[str]

    user: Mapped["User"] = relationship("User", back_populates="members")
    team: Mapped["Team"] = relationship("Team", back_populates="members")


class Invite(Base):
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    invite_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    team: Mapped["Team"] = relationship("Team", back_populates="invites")
    user: Mapped["User"] = relationship("User", back_populates="invites")




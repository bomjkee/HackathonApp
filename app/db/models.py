from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, ForeignKey, String, Boolean, DateTime, func, TIMESTAMP
from datetime import datetime
from typing import Optional, List

from app.db.database import Base


class User(Base):
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    full_name: Mapped[Optional[str]]

    photo_url: Mapped[Optional[str]]
    auth_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    hash: Mapped[Optional[str]]

    fio: Mapped[Optional[str]]
    is_mirea_student: Mapped[Optional[bool]]
    passport: Mapped[Optional[str]]

    members: Mapped[List["Member"]] = relationship("Member", back_populates="user")


class Team(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    is_open: Mapped[bool]

    hackathon_id: Mapped[int] = mapped_column(Integer, ForeignKey("hackathons.id"))

    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="teams")
    members: Mapped[List["Member"]] = relationship("Member", back_populates="team")


class Hackathon(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    max_members: Mapped[int]
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP)

    teams: Mapped[List["Team"]] = relationship("Team", back_populates="hackathon")


class Member(Base):
    member_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"))
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"))
    role: Mapped[Optional[str]]

    user: Mapped["User"] = relationship("User", back_populates="members")
    team: Mapped["Team"] = relationship("Team", back_populates="members")


from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from typing import Optional, List
from app.db.database import Base

class User(Base):
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]

    students: Mapped[List["Student"]] = relationship("Student", back_populates="user")
    non_students: Mapped[List["NonStudent"]] = relationship("NonStudent", back_populates="user")


class Student(Base):
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.tg_id'), primary_key=True)
    group: Mapped[Optional[str]]

    user: Mapped["User"] = relationship("User", back_populates="students")


class NonStudent(Base):
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.tg_id'), primary_key=True)
    passport: Mapped[Optional[str]]

    user: Mapped["User"] = relationship("User", back_populates="non_students")
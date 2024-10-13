from enum import unique

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey

from typing import Optional
from app.database import Base


class User(Base):
    id: Mapped[int] = mapped_column(int, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    patronymic: Mapped[Optional[str]]
    referral_id: Mapped[Optional[int]]
    is_student: Mapped[Optinal[bool]]

    def __str__(self):
        return (f"{self.__class__.__name__}(tg_id={self.id}, "
                f"first_name={self.first_name!r}, "
                f"last_name={self.last_name!r}), "
                f"patronymic={self.patronymic!r}")

    def __repr__(self):
        return str(self)


class Student(User):
    id: Mapped[int] = mapped_column(int, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False, unique=True)
    group: Mapped[Optional[str]]
    user: Mapped[User] = relationship('User', back_populates='student')


class NonStudent(User):
    id: Mapped[int] = mapped_column(int, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False, unique=True)
    passport: Mapped[Optional[str]]

from typing import Optional
from pydantic import BaseModel


class RBUser(BaseModel):
    def __init__(self, tg_id: int, username: str | None = None,
                 full_name: str | None = None, photo_url: str | None = None,
                 auth_date: str | None = None, hash: str | None = None,
                 fio: str | None = None, is_mirea_student: bool | None = None,
                 passport: str | None = None):
        self.tg_id = tg_id
        self.username = username
        self.full_name = full_name
        self.photo_url = photo_url
        self.auth_date = auth_date
        self.hash = hash
        self.fio = fio
        self.is_mirea_student = is_mirea_student
        self.passport = passport

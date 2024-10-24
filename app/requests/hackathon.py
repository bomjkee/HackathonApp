from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict


class RBHackathon(BaseModel):
    def __init__(self, name: str, description: str, max_members: int, start_date: str):
        self.name = name
        self.description = description
        self.max_members = max_members
        self.start_date = start_date
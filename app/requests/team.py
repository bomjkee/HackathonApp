from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict

class RBTeam(BaseModel):
    def __init__(self, name: str, is_open: bool):
        self.name = name
        self.is_open = is_open

class RBMember(BaseModel):
    def __init__(self, user_id: int, team_id: int,
                 role: str | None = None):
        self.user_id = user_id
        self.team_id = team_id
        self.role = role
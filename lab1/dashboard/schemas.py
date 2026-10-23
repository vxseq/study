from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TaskStatus = Literal["В работе", "Готово", "Блокер"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class ProjectResponse(ProjectCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)


class UserResponse(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    status: TaskStatus = "В работе"
    deadline: datetime | None = None
    project_id: int
    user_id: int | None = None

    @field_validator("deadline")
    @classmethod
    def convert_timezone(cls, value: datetime | None) -> datetime | None:
        # Если дата пришла с часовым поясом, переводим в местное время.
        if value is not None and value.tzinfo is not None:
            return value.astimezone().replace(tzinfo=None)
        return value


class TaskResponse(TaskCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

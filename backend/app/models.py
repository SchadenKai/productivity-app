import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
import uuid

class ProjectBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)

class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="project", cascade="all, delete-orphan")

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: uuid.UUID

class TaskBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    due_date: Optional[datetime] = None
    is_completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id")
    project: Optional[Project] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    project_id: uuid.UUID

class TaskRead(TaskBase):
    id: uuid.UUID
    project_id: uuid.UUID

# Habit Management Models
class HabitBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    timezone: str = Field(default="UTC", max_length=50)
    reset_time: str = Field(default="06:00", max_length=5)  # Format: "HH:MM"
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Habit(HabitBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: User = Relationship(back_populates="habits")
    streak: int = Field(default=0)
    last_completed: datetime | None = None

class HabitCreate(HabitBase):
    pass

class HabitUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    reset_time: str | None = Field(default=None, max_length=5)
    timezone: str | None = Field(default=None, max_length=50)
    is_completed: bool | None = None

class HabitPublic(HabitBase):
    id: uuid.UUID
    streak: int
    completion_rate: float = 0.0
    last_completed: datetime | None

# Add habits relationship to User model
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    habits: list["Habit"] = Relationship(back_populates="user", cascade_delete=True)
"""Declarative ORM base and a generic timestamped model mixin."""

from __future__ import annotations

from .mixins import TimestampMixin

import datetime

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Column, String, Text,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship

class BaseModel(DeclarativeBase):
    """Declarative base shared by all ORM model classes.

    Every concrete model should inherit from :class:`BaseModel` and define
    its own ``__tablename__`` and columns.  Common audit columns
    (``id``, ``created_at``, ``updated_at``) are provided via
    :class:`TimestampMixin`.

    Example::

        class Item(BaseModel, TimestampMixin):
            __tablename__ = "items"

            name: Mapped[str]
    """

# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(50), unique=True, nullable=False)
    name       = Column(String(100), nullable=True)
    email      = Column(String(120), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)  # store hashed passwords only!
    is_admin   = Column(Boolean, default=False)  # True = admin, False = standard user

    # Relationships
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete")
    created_tasks  = relationship("Task", back_populates="creator", cascade="all, delete")
    assignments    = relationship("Assignment", back_populates="user", cascade="all, delete-orphan")
    collaborator_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
class Project(BaseModel, TimestampMixin):
    __tablename__ = "projects"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    collaborator_memberships = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task(BaseModel, TimestampMixin):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status      = Column(
                    Enum("todo", "in_progress", "done", name="task_status"),
                    default="todo",
                    nullable=False
                  )
    priority    = Column(
                    Enum("low", "medium", "high", name="task_priority"),
                    default="medium",
                    nullable=False
                  )
    due_date    = Column(DateTime, nullable=True)
    project_id  = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    project     = relationship("Project", back_populates="tasks")
    creator     = relationship("User", back_populates="created_tasks")
    assignments = list["Assignment"] = relationship("Assignment", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# Assignment  (many-to-many bridge: Tasks ↔ Users)
# ---------------------------------------------------------------------------
class Assignment(BaseModel):
    __tablename__ = "assignments"
    __table_args__ = (UniqueConstraint("task_id", "user_id", name="uq_task_assignment"),)

    id          = Column(Integer, primary_key=True, index=True)
    task_id     = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    task = relationship("Task", back_populates="assignments")
    user = relationship("User", back_populates="assignments")

    def __repr__(self):
        return f"<Assignment task_id={self.task_id} user_id={self.user_id}>"
        
# ---------------------------------------------------------------------------
# ProjectMember (project collaborators)
# ---------------------------------------------------------------------------
class ProjectMember(BaseModel, TimestampMixin):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="collaborator_memberships")
    user = relationship("User", back_populates="collaborator_memberships")

    def __repr__(self):
        return f"<ProjectMember project_id={self.project_id} user_id={self.user_id}>"

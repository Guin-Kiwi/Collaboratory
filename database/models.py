"""Declarative ORM base and a generic timestamped model mixin."""

from __future__ import annotations

from .mixins import TimestampMixin

import datetime

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column, String, Text,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship


class BaseModel(DeclarativeBase):
    """Declarative base shared by all ORM model classes.

    Every concrete model should inherit from :class:`BaseModel` and define
    its own ``__tablename__`` and columns. Common audit columns
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
    """Represents a registered user of the application.

    Users can own projects, create tasks, be assigned to tasks,
    and collaborate on projects. Admin users have elevated permissions
    to manage other users and perform restricted actions.

    Attributes:
        id: Primary key.
        username: Unique login handle, max 50 characters.
        name: Optional full name, max 100 characters.
        email: Unique email address, max 120 characters.
        password: Bcrypt-hashed password string.
        is_admin: True if the user has admin privileges.
    """

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
        """Return a developer-friendly string representation of the user."""
        return f"<User id={self.id} username={self.username!r}>"


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
class Project(BaseModel, TimestampMixin):
    """Represents a project owned by a user.

    Projects contain tasks and notes, and can have collaborators
    added via ProjectMember. Only the owner can edit or delete
    the project and manage collaborators.

    Attributes:
        id: Primary key.
        name: Project name, max 100 characters.
        description: Optional longer description of the project.
        owner_id: Foreign key referencing the User who owns this project.
    """

    __tablename__ = "projects"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    notes = relationship("ProjectNote", back_populates="project", cascade="all, delete")
    collaborator_memberships = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        """Return a developer-friendly string representation of the project."""
        return f"<Project id={self.id} name={self.name!r}>"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task(BaseModel, TimestampMixin):
    """Represents a task within a project.

    Tasks have a status and priority, can be assigned to multiple users
    via Assignment, and can have notes attached. Tasks belong to exactly
    one project and are created by one user.

    Attributes:
        id: Primary key.
        title: Short task title, max 200 characters.
        description: Optional longer description of the task.
        status: Current status — one of 'todo', 'in_progress', 'completed'.
        priority: Task priority — one of 'low', 'medium', 'high'.
        due_date: Optional deadline for the task.
        project_id: Foreign key referencing the parent Project.
        created_by: Foreign key referencing the User who created the task.
    """

    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status      = Column(
                    Enum("todo", "in_progress", "completed", name="task_status"),
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
    assignments = relationship("Assignment", back_populates="task", cascade="all, delete-orphan")
    notes       = relationship("TaskNote", back_populates="task", cascade="all, delete")

    def __repr__(self):
        """Return a developer-friendly string representation of the task."""
        return f"<Task id={self.id} title={self.title!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# Assignment  (many-to-many bridge: Tasks ↔ Users)
# ---------------------------------------------------------------------------
class Assignment(BaseModel):
    """Represents the assignment of a user to a task.

    Acts as a many-to-many bridge between Task and User. A unique
    constraint prevents the same user from being assigned to the
    same task more than once.

    Attributes:
        id: Primary key.
        task_id: Foreign key referencing the assigned Task.
        user_id: Foreign key referencing the assigned User.
        assigned_at: Timestamp set automatically by the database on insertion.
    """

    __tablename__ = "assignments"
    __table_args__ = (UniqueConstraint("task_id", "user_id", name="uq_task_assignment"),)

    id          = Column(Integer, primary_key=True, index=True)
    task_id     = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    task = relationship("Task", back_populates="assignments")
    user = relationship("User", back_populates="assignments")

    def __repr__(self):
        """Return a developer-friendly string representation of the assignment."""
        return f"<Assignment task_id={self.task_id} user_id={self.user_id}>"

# ----
# The ProjectMember class is now in collab_models.py
# ----
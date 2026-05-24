"""Collaboration-related ORM models: project members and notes."""

from database.models import BaseModel
from database.mixins import TimestampMixin
from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


# ---------------------------------------------------------------------------
# ProjectMember (project collaborators)
# ---------------------------------------------------------------------------
class ProjectMember(BaseModel):
    """Represents a user's membership as a collaborator on a project.

    Acts as a many-to-many bridge between Project and User. A unique
    constraint prevents the same user from being added to the same
    project more than once. Admins and project owners are excluded
    from this table — they have implicit access.

    Attributes:
        id: Primary key.
        project_id: Foreign key referencing the Project.
        user_id: Foreign key referencing the collaborating User.
    """

    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    id         = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="collaborator_memberships")
    user    = relationship("User", back_populates="collaborator_memberships")

    def __repr__(self):
        """Return a developer-friendly string representation of the membership."""
        return f"<ProjectMember project_id={self.project_id} user_id={self.user_id}>"


# ---------------------------------------------------------------------------
# ProjectNote
# ---------------------------------------------------------------------------
class ProjectNote(BaseModel, TimestampMixin):
    """Represents a note attached to a project.

    Notes can be created by the project owner or collaborators,
    depending on permissions. Authors can always edit and delete
    their own notes. Users with the DELETE_PROJECT_NOTE permission
    can delete any note on the project.

    Attributes:
        id: Primary key.
        content: The text content of the note.
        project_id: Foreign key referencing the parent Project.
        created_by: Foreign key referencing the User who wrote the note.
    """

    __tablename__ = "project_notes"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="notes")
    author  = relationship("User")

    def __repr__(self):
        """Return a developer-friendly string representation of the project note."""
        return f"<ProjectNote id={self.id} project_id={self.project_id}>"


# ---------------------------------------------------------------------------
# TaskNote
# ---------------------------------------------------------------------------
class TaskNote(BaseModel, TimestampMixin):
    """Represents a note attached to a task.

    Notes can be created by users assigned to the task or with
    write permission. Authors can always edit and delete their own
    notes. Users with the DELETE_TASK_NOTE permission can delete
    any note on the task.

    Attributes:
        id: Primary key.
        content: The text content of the note.
        task_id: Foreign key referencing the parent Task.
        created_by: Foreign key referencing the User who wrote the note.
    """

    __tablename__ = "task_notes"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    task_id    = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    task   = relationship("Task", back_populates="notes")
    author = relationship("User")

    def __repr__(self):
        """Return a developer-friendly string representation of the task note."""
        return f"<TaskNote id={self.id} task_id={self.task_id}>"

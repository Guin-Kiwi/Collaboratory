from database.models import BaseModel
from database.mixins import TimestampMixin
from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


# ---------------------------------------------------------------------------
# ProjectMember (project collaborators)
# ---------------------------------------------------------------------------
class ProjectMember(BaseModel):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    id         = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="collaborator_memberships")
    user    = relationship("User", back_populates="collaborator_memberships")

    def __repr__(self):
        return f"<ProjectMember project_id={self.project_id} user_id={self.user_id}>"


# ---------------------------------------------------------------------------
# ProjectNote
# ---------------------------------------------------------------------------
class ProjectNote(BaseModel, TimestampMixin):
    __tablename__ = "project_notes"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="notes")
    author  = relationship("User")

    def __repr__(self):
        return f"<ProjectNote id={self.id} project_id={self.project_id}>"


# ---------------------------------------------------------------------------
# TaskNote
# ---------------------------------------------------------------------------
class TaskNote(BaseModel, TimestampMixin):
    __tablename__ = "task_notes"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    task_id    = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    task   = relationship("Task", back_populates="notes")
    author = relationship("User")

    def __repr__(self):
        return f"<TaskNote id={self.id} task_id={self.task_id}>"

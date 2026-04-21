"""
Permissions Manager

Authenticates users for interactions
"""
import enum

from sqlalchemy.orm import Session
from database.models import ProjectMember, Assignment 


class PermissionAction(enum.Enum):
    VIEW_PROJECT = "view_project"
    WRITE_PROJECT_NOTE = "write_project_note" # project NOTES for owners and collaborators only
    ADD_COLLABORATOR = "add_collaborator" # adding collaborators is done by owners only 
                                        #(collaborators can assign other users to tasks)
    CREATE_TASK = "create_task"
    EDIT_TASK_DETAILS = "edit_task_details" # title / description
    ASSIGN_TASK = "assign_task" # assigning users to tasks is done by owners or collaborators
    VIEW_TASK = "view_task" # Tasks are viewable by owners and collaborators not assigned to the task 
    CHANGE_TASK_STATUS = "change_task_status" # task statuses are logged as EVENTS (by the system)
    WRITE_TASK_NOTE = "write_task_note" # NOTES are how progress is logged

class PermissionDenied(Exception):
    def __init__(self, action: PermissionAction):
        super().__init__(f"Permission denied: {action.value}")
        self.action = action

def is_owner(user, project) -> bool:
    return project.owner_id == user.id

def is_collaborator(user, project, session: Session) -> bool:
    return session.query(ProjectMember).filter_by(
        project_id = project.id,
        user_id = user.id
        ).first() is not None

def is_assignee_on_task(user, task) -> bool:
    """User is assigned to this specific task."""
    return any(a.user_id == user.id for a in task.assignments)

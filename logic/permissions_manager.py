"""
Permissions Manager

Authenticates users for interactions
"""
import enum

from sqlalchemy.orm import Session
from database.models import User, Assignment, Project, Task
from database.collab_models import ProjectMember


class PermissionAction(enum.Enum):
    # Project
    CREATE_PROJECT      = "create_project"
    VIEW_PROJECT        = "view_project"
    EDIT_PROJECT_DETAILS = "edit_project"
    CHANGE_PROJECT_STATUS = "change_project_status"
    DELETE_PROJECT      = "delete_project"

    # Collaborators
    ADD_COLLABORATOR    = "add_collaborator"        # owner only

    # Project Notes
    VIEW_PROJECT_NOTE   = "view_project_note"       # owners and collaborators
    WRITE_PROJECT_NOTE  = "write_project_note"      # owners and collaborators
    DELETE_PROJECT_NOTE = "delete_project_note"     # TODO

    # Tasks
    CREATE_TASK         = "create_task"
    VIEW_TASK           = "view_task"               # owners, collaborators, and assignees
    EDIT_TASK_DETAILS   = "edit_task_details"       # title / description
    CHANGE_TASK_STATUS  = "change_task_status"      # assignees only
    ASSIGN_TASK         = "assign_task"             # owners and collaborators
    DELETE_TASK         = "delete_task"

    # Task Notes
    VIEW_TASK_NOTE      = "view_task_note"          # owners, collaborators, and assignees
    WRITE_TASK_NOTE     = "write_task_note"         # assignees only
    DELETE_TASK_NOTE    = "delete_task_note"        # TODO

class PermissionDenied(Exception):
    def __init__(self, action: PermissionAction):
        super().__init__(f"Permission denied: {action.value}")
        self.action = action

# --- Checker functions: Checking for true or false to assign users permissions ---        

def is_owner(user, project) -> bool:
    """user is assigned as the Project Owner (for when a user creates a project)"""
    return project.owner_id == user.id

def is_collaborator(user, project, session: Session) -> bool:
    """user is assigned as a Collaborator (owners can add users with collaborator attribute: collaborators can assign users to tasks)"""
    return session.query(ProjectMember).filter_by(
        project_id = project.id,
        user_id = user.id
        ).first() is not None

def is_assignee_on_task(user: User, task: Task) -> bool:
    """user is assigned to this specific Task."""
    return any(a.user_id == user.id for a in task.assignments)

def is_assignee_in_project(user : User, project : Project, session: Session) -> bool:
    """user is assigned to at least one Task in this project."""
    return session.query(Assignment).filter(
        Assignment.user_id == user.id,
        Assignment.task.has(project_id = project.id),
    ).first() is not None

#  --- core functions of the permission manager ---

def check_permission(
    user: User, 
    action: PermissionAction, 
    session: Session, 
    *,
    task: Task = None,
    project: Project = None
) -> bool:
    match action:
        case PermissionAction.CREATE_PROJECT:
            if user is None:
                return False

        case PermissionAction.VIEW_PROJECT:
            if project is None:
                return False
            return (
                user.is_admin
                or is_owner(user, project)
                or is_collaborator(user, project, session)
                or is_assignee_in_project(user, project, session)
            )
        
        case PermissionAction.CHANGE_PROJECT_STATUS:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )

        case PermissionAction.EDIT_PROJECT_DETAILS:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )
        
        case PermissionAction.WRITE_PROJECT_NOTE:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )
                
        case PermissionAction.VIEW_PROJECT_NOTE:
            if project is None:
                return False
            return (
                user.is_admin
                or is_owner(user, project)
                or is_collaborator(user, project, session)
                or is_assignee_in_project(user, project, session)
            )

        case PermissionAction.DELETE_PROJECT_NOTE:
            pass  # TODO

        case PermissionAction.DELETE_PROJECT:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project)
            )
        
        case PermissionAction.ADD_COLLABORATOR:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project)
            )
        
        case PermissionAction.ASSIGN_TASK:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, task.project) 
                or is_collaborator(user, task.project, session)
            )

        case PermissionAction.CREATE_TASK:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, task.project) 
                or is_collaborator(user, task.project, session)
            )

        case PermissionAction.VIEW_TASK:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, task.project) 
                or is_assignee_on_task(user, task) 
                or is_collaborator(user, task.project, session)
            )
        
        case PermissionAction.CHANGE_TASK_STATUS:
            if task is None:
                return False
            return (user.is_admin or is_assignee_on_task(user, task))

        case PermissionAction.VIEW_TASK_NOTE:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_assignee_on_task(user, task) 
                or is_owner(user, task.project) 
                or is_collaborator(user, task.project, session)
            )

        case PermissionAction.WRITE_TASK_NOTE:
            if task is None:
                return False
            return (user.is_admin or is_assignee_on_task(user, task))

        case PermissionAction.DELETE_TASK_NOTE:
            pass  # TODO

        case PermissionAction.EDIT_TASK_DETAILS:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, task.project) 
                or is_collaborator(user, task.project, session)
            )

        case PermissionAction.DELETE_TASK:
            if task is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, task.project) 
                or is_collaborator(user, task.project, session)
            )
        
        case _:
            return False

#-------------------------------------------------------------------

"""Call this require_permission function at the top of any write method.  Raises PermissionDenied if not allowed"""

#-------------------------------------------------------------------
def require_permission(
        user: User,
        action: PermissionAction,
        session: Session,
        *,
        task: Task = None,
        project: Project = None
) -> None:
    if not check_permission(user, action, session, project = project, task = task):
        raise PermissionDenied(action)
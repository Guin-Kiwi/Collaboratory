"""
Permissions Manager

Authenticates users for interactions
"""
import enum

from sqlalchemy.orm import Session
from database.models import User, Assignment, Project, Task
from database.collab_models import ProjectMember


class PermissionAction(enum.Enum):
    CREATE_PROJECT = "create_project"
    VIEW_PROJECT = "view_project"
    CHANGE_PROJECT_STATUS = "change_project_status"
    EDIT_PROJECT_DETAILS = "edit_project"
    DELETE_PROJECT = "delete_project"
    WRITE_PROJECT_NOTE = "write_project_note" # project NOTES for owners and collaborators only
    VIEW_PROJECT_NOTE = "view_project_note" # project NOTES
    ADD_COLLABORATOR = "add_collaborator" # adding collaborators is done by owners only 
                                        #(collaborators can assign other users to tasks)
    CREATE_TASK = "create_task"
    EDIT_TASK_DETAILS = "edit_task_details" # title / description
    ASSIGN_TASK = "assign_task" # assigning users to tasks is done by owners or collaborators
    VIEW_TASK = "view_task" # Tasks are viewable by owners and collaborators not assigned to the Taskask 
    CHANGE_TASK_STATUS = "change_task_status" # Taskask statuses are logged as EVENTS (by the system)
    WRITE_TASK_NOTE = "write_task_note" # NOTES are how progress is logged
    VIEW_TASK_NOTE = "view_task_note" # NOTES are how progress is logged
    DELETE_TASK = "delete_task" # Tasks can be deleted

class PermissionDenied(Exception):
    def __init__(self, action: PermissionAction):
        super().__init__(f"Permission denied: {action.value}")
        self.action = action

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
    return session.query(Assignment).join(Assignment.task).filter(
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
            return user is not None

        case PermissionAction.VIEW_PROJECT:
            return (
                user.is_admin
                or is_owner(user, project)
                or is_collaborator(user, project, session)
                or is_assignee_in_project(user, project, session)
            )
        
        case PermissionAction.CHANGE_PROJECT_STATUS:
            return user.is_admin or is_owner(user, project) #or is_collaborator(user, project, session)

        case PermissionAction.EDIT_PROJECT_DETAILS:
            return user.is_admin or is_owner(user, project) #or is_collaborator(user, project, session)
        
        case PermissionAction.WRITE_PROJECT_NOTE:
            return user.is_admin or is_owner(user, project) or is_collaborator(user, project, session)
                
        case PermissionAction.VIEW_PROJECT_NOTE:
            return user.is_admin or is_owner(user, project) or is_collaborator(user, project, session)
    
        case PermissionAction.DELETE_PROJECT:
            return user.is_admin or is_owner(user, project)
        
        case PermissionAction.ADD_COLLABORATOR:
            return user.is_admin or is_owner(user, project)
        
        case PermissionAction.ASSIGN_TASK:
            return user.is_admin or is_owner(user, task.project) #or is_collaborator(user, task.project, session)

        case PermissionAction.CREATE_TASK:
            return user.is_admin or is_owner(user, task.project) #or is_collaborator(user, task.project, session)
        
        case PermissionAction.VIEW_TASK:
            return user.is_admin or is_owner(user, task.project) or is_assignee_on_task(user, task) #or is_collaborator(user, task.project, session)
        
        case PermissionAction.CHANGE_TASK_STATUS:
            return user.is_admin or is_assignee_on_task(user, task)

        case PermissionAction.VIEW_TASK_NOTE:
            return user.is_admin or is_assignee_on_task(user, task) or is_owner(user, task.project) or is_collaborator(user, task.project, session)

        case PermissionAction.WRITE_TASK_NOTE:
            return user.is_admin or is_assignee_on_task(user, task)
        
        case PermissionAction.EDIT_TASK_DETAILS:
            return user.is_admin or is_owner(user, task.project) #or is_collaborator(user, task.project, session)
        
        case PermissionAction.DELETE_TASK:
            return user.is_admin or is_owner(user, task.project) #or is_collaborator(user, task.project, session)
        
        case _:
            return False

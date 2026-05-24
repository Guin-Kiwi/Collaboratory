"""
Permissions Manager

Enforces role-based access control across all write and read operations.

Roles (in order of trust):
  admin       — is_admin flag on User; bypasses all checks
  owner       — created the project (project.owner_id)
  collaborator — added to ProjectMember by the owner; can assign tasks and manage notes
  assignee    — assigned to a specific task via Assignment; can update that task's status and write task notes
  (no role)   — can only create new projects; denied access to all existing project content

All write operations call require_permission(), which raises PermissionDenied on failure.
UI visibility checks call check_permission() to conditionally show/hide buttons.
"""
import enum

from sqlalchemy.orm import Session
from database.models import User, Assignment, Project, Task
from database.collab_models import ProjectMember


class PermissionAction(enum.Enum):
    """Enumeration of all permission-gated actions in the system."""

    # --- Projects ---
    CREATE_PROJECT        = "create_project"         # all authenticated users
    VIEW_PROJECT          = "view_project"            # admin, owner, collaborator, any assignee
    EDIT_PROJECT_DETAILS  = "edit_project"            # admin, owner, collaborator  (name, description)
    CHANGE_PROJECT_STATUS = "change_project_status"  # admin, owner, collaborator
    DELETE_PROJECT        = "delete_project"          # admin, owner

    # --- Collaborators ---
    MANAGE_COLLABORATOR   = "manage_collaborator"      # admin, owner (covers add and remove)
    # Note: admins and the project owner cannot themselves be added (enforced in collab_manager)

    # --- Project Notes ---
    VIEW_PROJECT_NOTE     = "view_project_note"       # admin, owner, collaborator, any assignee
    WRITE_PROJECT_NOTE    = "write_project_note"      # admin, owner, collaborator
    DELETE_PROJECT_NOTE   = "delete_project_note"     # admin, owner  (collaborators may delete their own via author bypass in collab_manager)

    # --- Tasks ---
    CREATE_TASK           = "create_task"             # admin, owner, collaborator
    VIEW_TASK             = "view_task"               # admin, owner, collaborator, task assignee
    EDIT_TASK_DETAILS     = "edit_task_details"       # admin, owner, collaborator  (title, description)
    CHANGE_TASK_STATUS    = "change_task_status"      # admin, task assignee only  (owners/collaborators must also be assigned)
    ASSIGN_TASK           = "assign_task"             # admin, owner, collaborator
    DELETE_TASK           = "delete_task"             # admin, owner, collaborator

    # --- Task Notes ---
    VIEW_TASK_NOTE        = "view_task_note"          # admin, owner, collaborator, task assignee
    WRITE_TASK_NOTE       = "write_task_note"         # admin, task assignee only  (owners/collaborators must also be assigned)
    DELETE_TASK_NOTE      = "delete_task_note"        # admin, owner, task assignee  (authors may also delete their own via author bypass in collab_manager)

class PermissionDenied(Exception):
    """Raised when a user attempts an action they are not permitted to perform."""

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

def is_assignee_on_task(user: User, task: Task, session: Session) -> bool:
    """user is assigned to this specific Task (DB-backed check)."""
    if task is None:
        return False
    return (
        session.query(Assignment)
        .filter(Assignment.user_id == user.id, Assignment.task_id == task.id)
        .first()
        is not None
    )

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
    """Return True if user is allowed to perform action, False otherwise."""
    if user is None:
        return False
    # If caller provided a task but not a project, resolve project by id
    if project is None and task is not None:
        proj_id = getattr(task, 'project_id', None)
        if proj_id is not None:
            project = session.query(Project).filter_by(id=proj_id).first()
    match action:
        case PermissionAction.CREATE_PROJECT:
            return True

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
            if project is None:
                return False
            return (
                user.is_admin
                or is_owner(user, project)
            )

        case PermissionAction.DELETE_PROJECT:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project)
            )
        
        case PermissionAction.MANAGE_COLLABORATOR:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project)
            )
        
        case PermissionAction.ASSIGN_TASK:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )

        case PermissionAction.CREATE_TASK:
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )

        case PermissionAction.VIEW_TASK:
            if task is None:
                return False
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_assignee_on_task(user, task, session)
                or is_collaborator(user, project, session)
            )
        
        case PermissionAction.CHANGE_TASK_STATUS:
            if task is None:
                return False
            return (user.is_admin or is_assignee_on_task(user, task, session))

        case PermissionAction.VIEW_TASK_NOTE:
            if task is None:
                return False
            if project is None:
                return False
            return (
                user.is_admin 
                or is_assignee_on_task(user, task, session) 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )

        case PermissionAction.WRITE_TASK_NOTE:
            if task is None:
                return False
            return (user.is_admin or is_assignee_on_task(user, task, session))

        case PermissionAction.DELETE_TASK_NOTE:
            if task is None:
                return False
            if project is None:
                return False
            return (user.is_admin 
                or is_owner(user, project) 
                or is_assignee_on_task(user, task, session))

        case PermissionAction.EDIT_TASK_DETAILS:
            if task is None:
                return False
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
            )

        case PermissionAction.DELETE_TASK:
            if task is None:
                return False
            if project is None:
                return False
            return (
                user.is_admin 
                or is_owner(user, project) 
                or is_collaborator(user, project, session)
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
    """Raise PermissionDenied if user is not allowed to perform action."""
    if not check_permission(user, action, session, project = project, task = task):
        raise PermissionDenied(action)

# logic/project_manager.py

from datetime import datetime

from database.models import Assignment, Task, User, Project
from database.collab_models import ProjectMember, ProjectNote
from database import db_conn
from logic.permissions_manager import require_permission, PermissionAction
from sqlalchemy.orm import joinedload

class ProjectManager:
    def __init__(self, session=None): 
        self.session = session or db_conn.get_session() 

###----------- helper functions for the project manager (e.g. get project by id, get projects by user, etc.) -----------
    
    def get_project_by_id(self, project_id: int) -> Project | None:
        return (
            self.session.query(Project)
            .options(
                joinedload(Project.collaborator_memberships).joinedload(ProjectMember.user),
                joinedload(Project.tasks).joinedload(Task.assignments).joinedload(Assignment.user),
                joinedload(Project.notes),
            )
            .filter_by(id=project_id)
            .first()
        )
    
    def get_projects_by_owner(self, user_id: int) -> list[Project]:
        """Get all projects owned by a user."""
        return self.session.query(Project).filter_by(owner_id=user_id).all()
    
    def get_projects_by_collaborator(self, user_id: int) -> list[Project]:
        """Get all projects a user is collaborating on."""
        return self.session.query(Project).join(ProjectMember).filter(ProjectMember.user_id == user_id).all()

    def get_projects_by_task_assignment(self, user_id: int) -> list[Project]:
        """Get all projects where the user is assigned to at least one task."""
        return (
            self.session.query(Project)
            .join(Task, Task.project_id == Project.id)
            .join(Assignment, Assignment.task_id == Task.id)
            .filter(Assignment.user_id == user_id)
            .distinct()
            .all()
        )


###----------- core functions of the project manager (e.g. CRUD ) -----------

    def create_project(
        self,
        user: User,
        name: str,
        description: str,
        owner_id: int,
        ) -> Project:
            """Create a new Project"""
            require_permission(user, PermissionAction.CREATE_PROJECT, self.session) 
            project = Project(
                name = name,
                description = description,
                owner_id = owner_id,
            )
            self.session.add(project)
            self.session.commit()
            return project

    def view_project(self, user: User, project_id: int) -> Project | None:
        """View a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return None

        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return project


    def edit_project_details(self, user: User, project_id: int, name: str, description: str) -> bool:
        """Edit a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        require_permission(user, PermissionAction.EDIT_PROJECT_DETAILS, self.session, project = project) 
        project.name = name
        project.description = description
        self.session.commit()
        return True

    def delete_project(self, user: User, project_id: int) -> bool:
        """Delete a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False
 
        require_permission(user, PermissionAction.DELETE_PROJECT, self.session, project = project)      
        self.session.delete(project)
        self.session.commit()
        return True


    def view_project_tasks(self, user: User, project_id: int) -> list[Task]:
        """View all tasks of a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return []
        
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return project.tasks






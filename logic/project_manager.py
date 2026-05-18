# logic/project_manager.py

from datetime import datetime

from database.models import Assignment, Task, User, Project
from database.collab_models import ProjectMember, ProjectNote
from database.connection import DatabaseConnection
from logic.permissions_manager import require_permission, PermissionAction

class ProjectManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.init()
        self.session = self.db.get_session()

###----------- helper functions for the project manager (e.g. get project by id, get projects by user, etc.) -----------
    
    def get_project_by_id(self, project_id: int) -> Project | None:
        """Get project by ID"""
        return self.session.query(Project).filter_by(id = project_id).first()
    
    def get_projects_by_user(self, user_id: int) -> list[Project]:
        """Get all projects of a user"""
        return self.session.query(Project).join(ProjectMember).filter(
            ProjectMember.user_id == user_id
        ).all()


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






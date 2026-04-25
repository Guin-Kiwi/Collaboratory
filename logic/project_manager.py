# logic/task_manager.py

from datetime import datetime

from database.models import Assignment, Task
from database.connection import DatabaseConnection

class ProjectManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.session = self.db.get_session()

    def create_project(
        self,
        user: User,
        title: str,
        description: str,
        owner_id: int,
        assignees: list[int] | None = None,
        tasks: list[Task] | None = None,
        ) -> Project:
            """Create a new Project"""
            require_permission(user, PermissionAction.CREATE_PROJECT, self.session) 
            project = Project(
                title = title,
                description = description,
                owner_id = owner_id,
            )
            self.session.add(project)
            self.session.commit()
            return project

    def edit_project_details(self, project_id: int, title: str, description: str) -> bool:
        """Edit a project"""
        require_permission(user, PermissionAction.EDIT_PROJECT_DETAILS, self.session, project = project) 
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        project.title = title
        project.description = description
        self.session.commit()
        return True

    def view_project(self, project_id: int) -> Project | None:
        """View a project"""
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return self.get_project_by_id(project_id)

    def edit_project_notes(self, project_id: int, content: str) -> bool:
        """Edit a project note"""
        require_permission(user, PermissionAction.WRITE_PROJECT_NOTE, self.session, project = project) 
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        
        note = ProjectNote(content=content, project_id=project_id, created_by=user.id)
        self.session.add(note)
        self.session.commit()
        return True
    
    def view_project_notes(self, project_id: int) -> list[ProjectNote]:
        """View notes of a project"""
        require_permission(user, PermissionAction.VIEW_PROJECT_NOTE, self.session, project = project) 
        project = self.get_project_by_id(project_id)
        if not project:
            return []
        return project.notes

    def add_collaborator(self, project_id: int, user_id: int) -> bool:
        """Add a collaborator to a project"""
        require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project) 
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        
        user = self.session.query(User).filter_by(id = user_id).first()
        if not user:
            return False
        
        membership = ProjectMember(user_id=user_id, project_id=project_id)
        self.session.add(membership)
        self.session.commit()
        return True

    def remove_collaborator(self, project_id: int, user_id: int) -> bool:
        """Remove a collaborator from a project"""
        require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project) 
        membership = self.session.query(ProjectMember).filter_by(
            user_id=user_id,
            project_id=project_id
        ).first()
        if not membership:
            return False
        
        self.session.delete(membership)
        self.session.commit()
        return True

    def get_project_by_id(self, project_id: int) -> Project | None:
        """Get project by ID"""
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return self.session.query(Project).filter_by(id = project_id).first()
    
    def get_projects_by_user(self, user_id: int) -> list[Project]:
        """Get all projects of a user"""
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return self.session.query(Project).join(ProjectMember).filter(
            ProjectMember.user_id == user_id
        ).first()

    def view_project_tasks(self, project_id: int) -> list[Task]:
        """View all tasks of a project"""
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        project = self.get_project_by_id(project_id)
        if not project:
            return []
        return project.tasks

    def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        require_permission(user, PermissionAction.DELETE_PROJECT, self.session, project = project) 
        if input(f"Are you sure you want to delete the project '{project.title}'? \n"
            "This action cannot be undone. (yes/no): "
        ) != "yes":
            print("Project deletion cancelled.")
            return False
        
        self.session.delete(project)
        self.session.commit()
        return True
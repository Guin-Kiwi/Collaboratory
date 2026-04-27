# logic/project_manager.py

from datetime import datetime

from database.models import Assignment, Task, User, Project, ProjectMember#, ProjectNote
from database.connection import DatabaseConnection
from logic.permissions_manager import require_permission, PermissionAction

class ProjectManager:
    def __init__(self):
        self.db = DatabaseConnection()
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
        title: str,
        description: str,
        owner_id: int,
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

    def view_project(self, user: User, project_id: int) -> Project | None:
        """View a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return None

        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return project


    def edit_project_details(self, user: User, project_id: int, title: str, description: str) -> bool:
        """Edit a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        require_permission(user, PermissionAction.EDIT_PROJECT_DETAILS, self.session, project = project) 
        project.title = title
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


## ------- functions related to project children (e.g. Notes and Tasks) -------
## IF ADDED, can Uncomment

    # def edit_project_notes(self, user: User, project_id: int, content: str) -> bool:
    #     """Edit a project note"""
    #     project = self.get_project_by_id(project_id)
    #     if not project:
    #         return False
 
    #     require_permission(user, PermissionAction.WRITE_PROJECT_NOTE, self.session, project = project) 
    #     note = ProjectNote(content=content, project_id=project_id, created_by=user.id)
    #     self.session.add(note)
    #     self.session.commit()
    #     return True
    
    # def view_project_notes(self, user: User, project_id: int) -> list[ProjectNote]:
    #     """View notes of a project"""
    #     project = self.get_project_by_id(project_id)
    #     if not project:
    #         return []

    #     require_permission(user, PermissionAction.VIEW_PROJECT_NOTE, self.session, project = project) 
    #     return project.notes

    def view_project_tasks(self, user: User, project_id: int) -> list[Task]:
        """View all tasks of a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return []
        
        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
        return project.tasks


## ------- functions related to project collaborators (e.g. add/remove collaborator, view collaborators) -------
## uncomment if used
## fix this 
# """1. add_collaborator and remove_collaborator — user gets overwritten
# Both methods receive user: User as a parameter (the person performing the action), but then immediately overwrite it:
# pythonuser = self.session.query(User).filter_by(id = user_id).first()
# Now when require_permission(user, ...) runs, user is the target collaborator, not the actor. The permission check runs on the wrong person.
# Rename the looked-up user to something like target_user to keep them separate."""


    # def add_collaborator(self, user: User, project_id: int, user_id: int) -> bool:
    #     """Add a collaborator to a project"""
    #     project = self.get_project_by_id(project_id)
    #     if not project:
    #         return False
        
    #     user = self.session.query(User).filter_by(id = user_id).first()
    #     if not user:
    #         return False     

    #     require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project) 
    #     membership = ProjectMember(project_id=project_id, user_id=user_id)
    #     self.session.add(membership)
    #     self.session.commit()
    #     return True

    # def view_collaborators(self, user: User, project_id: int) -> list[User]:
    #     """View collaborators of a project"""
    #     project = self.get_project_by_id(project_id)
    #     if not project:
    #         return []

    #     require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project) 
    #     return [membership.user for membership in project.collaborator_memberships]

    # def remove_collaborator(self, user: User, project_id: int, user_id: int) -> bool:
    #     """Remove a collaborator from a project"""
    #     project = self.get_project_by_id(project_id)
    #     if not project:
    #         return False   

    #     user = self.session.query(User).filter_by(id = user_id).first()
    #     if not user:
    #         return False  

    #     membership = self.session.query(ProjectMember).filter_by(
    #         user_id=user_id,
    #         project_id = project_id,
    #     ).first()
    #     if not membership:
    #         return False

    #     require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project) 
     #    self.session.delete(membership)
      #   self.session.commit()
       #  return True




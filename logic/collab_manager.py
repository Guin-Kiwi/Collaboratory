from datetime import datetime

from database.models import User, Project, Task, Assignment
from database.collab_models import ProjectNote as PNote, TaskNote as TNote, ProjectMember as PMember
from database.connection import DatabaseConnection
from logic.permissions_manager import require_permission, PermissionAction


class CollabManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.init()
        self.session = self.db.get_session()

#------- helper functions for the collaboration association

    def get_project_list_as_collaborator(self, user_id: int) -> list[Project]:
        return (
            self.session.query(Project)
            .join(PMember, PMember.project_id == Project.id)
            .filter(PMember.user_id == user_id)
            .all()
        )

    def get_project_by_id(self, project_id: int) -> Project:
        return (
            self.session.query(Project).filter_by(id=project_id).first()
        )



#------ core functions
    
    def view_collaborators(self, user: User, project_id: int) -> list[User]:
        """View collaborators of a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return []

        require_permission(user, PermissionAction.VIEW_PROJECT, self.session, project = project)
        return [membership.user for membership in project.collaborator_memberships]

    def add_collaborator(self, user: User, project_id: int, user_id: int) -> bool:
        """Add a collaborator to a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        target_user = self.session.query(User).filter_by(id = user_id).first()
        if not target_user:
            return False
        if (target_user.is_admin
            or target_user.id == user.id 
            or target_user.id == project.owner_id 
            or target_user in project.collaborator_memberships
        ):
            return False

        require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project)
        membership = PMember(project_id=project_id, user_id=user_id)
        self.session.add(membership)
        self.session.commit()
        return True

    def remove_collaborator(self, user: User, project_id: int, user_id: int) -> bool:
        """Remove a collaborator from a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        target_user = self.session.query(User).filter_by(id = user_id).first()
        if not target_user:
            return False

        membership = self.session.query(PMember).filter_by(
            user_id=user_id,
            project_id = project_id,
        ).first()
        if not membership:
            return False

        require_permission(user, PermissionAction.ADD_COLLABORATOR, self.session, project = project)
        self.session.delete(membership)
        self.session.commit()
        return True


#---------- Project and Task Note CRUD functions

    def create_project_note(self, user : User, content: str) -> bool:
        """Create a project note"""
        if user is None:
            return False

        require_permission(user, PermissionAction.WRITE_PROJECT_NOTE, self.session, project = project)
        note = PNote(content = content, project_id = project_id, created_by = user.id)
        self.session.add(note)
        self.session.commit()
        return True

    def edit_project_note(self, user: User, project_id: int, pnote_id: int, content: str) -> bool:
        """Edit a project note"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        note = self.session.query(PNote).filter_by(id = pnote_id).first()
        if not note:
            return False

        if not note.created_by == user.id:
            return False

        require_permission(user, PermissionAction.WRITE_PROJECT_NOTE, self.session, project = project)
        note.content = content
        self.session.commit()
        return True

    def view_project_note(self, user: User, project_id: int) -> list[PNote]:
        """View notes of a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return []

        require_permission(user, PermissionAction.VIEW_PROJECT_NOTE, self.session, project = project)
        return project.notes

    def delete_project_note(self, user: User, project_id: int, pnote_id: int) -> bool :
        """Delete notes of a Project"""
        project = self.get_project_by_id(project_id = project_id)
        if not project:
            return False

        target_note=self.session.query(PNote).filter_by(id = pnote_id).first()
        if not target_note:
            return False
        
        if not (target_note.created_by == user.id 
            or user.is_admin
            or project.owner_id == user.id
        ):
            return False

        require_permission(user, PermissionAction.DELETE_PROJECT_NOTE, self.session, project = project)
        self.session.delete(target_note)
        self.session.commit()
        return True

    def create_task_note(self, user: User, task_id: int, content: str) -> bool:
        """Create a task note"""
        task = self.session.query(Task).filter_by(id = task_id).first()
        if not task:
            return False

        require_permission(user, PermissionAction.WRITE_TASK_NOTE, self.session, task = task)
        note = TNote(content = content, task_id = task_id, created_by = user.id)
        self.session.add(note)
        self.session.commit()
        return True

    def edit_task_note(self, user: User, task_id: int, tnote_id: int, content: str) -> bool:
        """Edit a task note"""
        task = self.session.query(Task).filter_by(id = task_id).first()
        if not task:
            return False
        note = self.session.query(TNote).filter_by(id = tnote_id).first()
        if not note:
            return False
        if not note.created_by == user.id:
            return False

        require_permission(user, PermissionAction.WRITE_TASK_NOTE, self.session, task = task)
        note.content = content
        self.session.commit()
        return True

    def delete_task_note(self, user: User, task_id: int, tnote_id: int) -> bool:
        """Delete note of a Task"""
        task = self.session.query(Task).filter_by(id = task_id).first()
        if not project:
            return False

        target_note = self.session.query(TNote).filter_by(id = tnote_id).first()
        if not target_note:
            return False

        if not (target_note.created_by == user.id 
            or user.is_admin
        ):
            return False

        require_permission(user, PermissionAction.DELETE_PROJECT_NOTE, self.session, project = project)
        self.session.delete(target_note)
        self.session.commit()
        return True
"""
Task Manager

Manages tasks: create, get, update, delete, assign, and change status.

Checks permissions so only allowed users can perform actions.
"""

from datetime import datetime

from database.models import Assignment, Task, User, Project
from database.connection import DatabaseConnection
from logic.permissions_manager import require_permission, PermissionAction


class TaskManager:

    def __init__(self):
        self.db = DatabaseConnection()
        self.session = self.db.get_session()

    def create_task(self, user: User, project: Project, title: str, description: str, due_date: datetime | None, priority: str, status: str,) -> Task:
        """Create a new task"""
        task = Task(
            title = title,
            description = description,
            created_by = user.id,
            project_id = project.id,
            due_date = due_date,
            priority = priority,
            status = status)
        require_permission(user, PermissionAction.CREATE_TASK, self.session, project = project, task = task)
       
        self.session.add(task)
        self.session.commit()
        return task

    def get_task_by_id(self, user: User, project: Project, task_id: int) -> Task | None:
        """Get task by ID"""
        task = self.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return None
        require_permission(user, PermissionAction.VIEW_TASK, self.session, project = project, task = task) 
        return task

    def get_tasks_by_user(self, user: User, project: Project, user_id: int) -> list[Task]:
        """Get all tasks of a user"""
        require_permission(user, PermissionAction.VIEW_TASK, self.session, project = project) 
        return self.session.query(Task).join(Assignment).filter(
            Assignment.user_id == user_id
        ).all()

    def update_task(self, user: User, project: Project, task_id: int, title: str, description: str,) -> bool:
        """Update a task"""
        task = self.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        require_permission(user, PermissionAction.EDIT_TASK_DETAILS, self.session, project = project, task = task)

        task.title = title
        task.description = description
        self.session.commit()
        return True

    def delete_task(self, user: User, project: Project, task_id: int) -> bool:
        """Delete a task"""
        task = self.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        require_permission(user, PermissionAction.DELETE_TASK, self.session, project = project, task = task)

        self.session.delete(task)
        self.session.commit()
        return True
    
    def assign_task(self, user: User, project: Project, task_id: int, assigned_user_id: int,) -> bool:
        """Assign a task to a user"""
        task = self.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        require_permission(user, PermissionAction.ASSIGN_TASK, self.session, project = project, task = task)

        assignment = Assignment(user_id = assigned_user_id, task_id = task_id)
        self.session.add(assignment)
        self.session.commit()
        return True

    def change_task_status(self, user: User, project: Project, task_id: int, status: str) -> bool:
        """Change the status of a task"""
        task = self.session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        require_permission(user, PermissionAction.CHANGE_TASK_STATUS, self.session, project = project, task = task)

        task.status = status
        self.session.commit()
        return True
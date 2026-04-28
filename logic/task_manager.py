# logic/task_manager.py

from datetime import datetime

from database.models import Assignment, Task, User
from database.connection import DatabaseConnection
from logic.permissions_manager import require_permission, PermissionAction


class TaskManager:

    def __init__(self):
        self.db = DatabaseConnection()
        self.session = self.db.get_session()

    def create_task(
        self,
        title: str,
        description: str,
        owner_id: int,
        project_id: int,
        due_date: datetime | None,
        priority: str,
        status: str,
    ) -> Task:
        """Create a new task"""
        require_permission(user, PermissionAction.CREATE_TASK, self.session, project) 
        task = Task(
            title = title,
            description = description,
            created_by = owner_id,
            project_id = project_id,
            due_date = due_date,
            priority = priority,
            status = status,
        )
        self.session.add(task)
        self.session.commit()
        return task

    def get_task_by_id(self, task_id: int) -> Task | None:
        """Get task by ID"""
        require_permission(user, PermissionAction.VIEW_TASK, self.session, task = task) 
        return self.session.query(Task).filter_by(id = task_id).first()

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        """Get all tasks of a user"""
        require_permission(user, self.session, PermissionAction.VIEW_TASK, self.session, task = task) 
        return self.session.query(Task).join(Assignment).filter(
            Assignment.user_id == user_id
        ).all()

    def update_task(self, task_id: int, title: str, description: str) -> bool:
        """Update a task"""
        require_permission(user, PermissionAction.EDIT_TASK_DETAILS, self.session, task = task) 
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.title = title
        task.description = description
        self.session.commit()
        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        require_permission(user, PermissionAction.DELETE_TASK, self.session, project = project, task = task) 
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
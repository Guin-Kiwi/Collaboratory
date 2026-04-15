# logic/task_manager.py

from database.models import Task
from database.connection import DatabaseConnection

class TaskManager:

    def __init__(self):
        self.db = DatabaseConnection()
        self.session = self.db.get_session()

    def create_task(self, title: str, description: str, owner_id: int, due_date: int, priority: str, status: str) -> Task:
        task = Task(
            title = title,
            description = description,
            owner_id = owner_id,
            due_date = due_date,
            priority = priority,
            status = status,
            is_completed = False,
        )
        self.session.add(task)
        self.session.commit()
        return task

    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.session.query(Task).filter_by(id = task_id).first()

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return self.session.query(Task).filter_by(owner_id = user_id).all()

    def update_task(self, task_id: int, title: str, description: str) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task.title = title
        task.description = description
        self.session.commit()
        return True

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
from nicegui import ui

from ui.view import BaseView
from ui.layout import project_frame
from logic.app_state import app_state
from database import db_conn
from database.models import Task


class TaskPage(BaseView):
    def render(self, task: Task) -> None:
        project_frame(page=task.title, user=app_state.get_current_user(), project=task.project)


@ui.page('/task/{task_id}')
def task(task_id: int) -> None:
    session = db_conn.get_session()
    task = session.query(Task).filter_by(id=task_id).first()
    if task is None:
        ui.label('Task not found.')
        return
    TaskPage().render(task)

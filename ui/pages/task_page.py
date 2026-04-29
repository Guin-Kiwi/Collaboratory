# --- FOR UI DEVELOPERS ---
# This page will need data from CollabManager (logic/collab_manager.py).
# Create an instance with: manager = CollabManager()
#
# Useful calls for the task page:
#   manager.create_task_note(user, task_id, content)
#       -> assignees only — lets an assignee log a progress note on this task
#   manager.view_project_note(user, project_id)
#       -> owners and collaborators can see project-level notes from this page too
#
# Permissions to be aware of (logic/permissions_manager.py):
#   - Only the task's assignees can write task notes or change task status
#   - Owners and collaborators can view task notes but cannot write them
#   - Task status is changed by assignees only — owners cannot override this
#
# The logged-in user is always available via: app_state.get_current_user()
# The current task is passed into TaskPage.render(task) — use task.id and task.project_id
# -------------------------

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

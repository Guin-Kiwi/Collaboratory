# # --- FOR UI DEVELOPERS ---
# To view this page locally:
#   1. Run: python main.py
#   2. Open: http://localhost:8080/task/1
#      (replace 1 with any valid task ID from the seeded database)
#
# ...rest of the existing collab manager notes...
# This page will need data from CollabManager (logic/collab_manager.py).
# Create an instance with: manager = CollabManager()
#
# The current task is passed into TaskPage.render(task) — use task.id to get the task ID.
# To get the project this task belongs to, use task.project.id
#
# Useful calls for the task page:
#   manager.view_task_note(user, task.id)
#       -> list of notes on this task (owners, collaborators, and assignees)
#   manager.create_task_note(user, task.id, content)
#       -> assignees only — lets an assignee log a progress note on this task
#   manager.edit_task_note(user, task.id, tnote_id, content)
#       -> assignees only — only the original author of the note can edit it
#   manager.delete_task_note(user, task.id, tnote_id)
#       -> the note author or an admin can delete it
#   manager.view_project_note(user, task.project.id)
#       -> owners and collaborators can see project-level notes from this page too
#
# Permissions to be aware of (logic/permissions_manager.py):
#   - Only the task's assignees can write or edit task notes
#   - Owners and collaborators can view task notes but cannot write them
#   - Task status is changed by assignees only — owners cannot override this
#
# The logged-in user is always available via: app_state.get_current_user()
# -------------------------

from nicegui import ui

from ui.view import BaseView
from ui.layout import task_frame
from logic.app_state import app_state
from database import db_conn
from database.models import Task, User


class TaskPage(BaseView):
    def render(self, task: Task) -> None:
        task_frame(page=task.title, user=app_state.get_current_user(), task = task)


@ui.page('/task/{task_id}')
def task(task_id: int) -> None:
    session = db_conn.get_session()
    task = session.query(Task).filter_by(id=task_id).first()
    if task is None:
        ui.label('Task not found.')
        return

    # TODO: remove once login is wired up
    # DEV BYPASS: auto-logs in as alice (admin user) so you can view this page directly.
    # To test as a different user, comment out this block and go to http://localhost:8080 first.
    if not app_state.is_authenticated():
        alice = session.query(User).filter_by(username="alice").first()
        app_state.login(alice)
    TaskPage().render(task)  #keep this though

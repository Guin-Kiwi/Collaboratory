"""
Task Page UI

Allows users to view and edit tasks and manage task notes.
Route: /task/{task_id}
"""

from nicegui import ui

from ui.view import BaseView
from ui.layout import task_frame
from logic.app_state import app_state
from logic.task_manager import TaskManager
from logic.collab_manager import CollabManager
from database import db_conn
from database.models import User, Project, Task


class TaskPage(BaseView):
    def render(self, task: Task) -> None:
        user = app_state.get_current_user()

        task_manager = TaskManager()
        collab_manager = CollabManager()

        task_frame(page=task.title, user=user, task=task)

        project = task.project

        ui.label("Task Details").classes("text-h6")

        ui.label(f"Title: {task.title}")
        ui.label(f"Description: {task.description or 'No description'}")
        ui.label(f"Status: {task.status}")
        ui.label(f"Priority: {task.priority}")

        ui.separator()

        # EDIT TASK
        with ui.dialog() as edit_task_dialog, ui.card():
            ui.label("Edit Task")

            title = ui.input("Title", value=task.title)

            description = ui.textarea(
                "Description",
                value=task.description or "",
            )

            status = ui.select(
                ["todo", "in_progress", "completed"],
                value=task.status,
                label="Status",
            )

            def save_task():
                if not title.value or not title.value.strip():
                    ui.notify("Title is required", type="negative")
                    return

                task_manager.update_task(
                    user=user,
                    project=project,
                    task_id=task.id,
                    title=title.value.strip(),
                    description=description.value or "",
                )

                task_manager.change_task_status(
                    user=user,
                    project=project,
                    task_id=task.id,
                    status=status.value,
                )

                ui.notify("Task updated", type="positive")

                edit_task_dialog.close()
                ui.navigate.reload()

            ui.button("Save", on_click=save_task)
            ui.button("Cancel", on_click=edit_task_dialog.close)

        ui.button("Edit Task", on_click=edit_task_dialog.open)

        ui.separator()

        # TASK NOTES
        ui.label("Task Notes").classes("text-h6")

        notes = collab_manager.view_task_note(user, task.id)

        for note in notes:
            ui.separator()

            ui.label(note.content)

            # EDIT NOTE
            with ui.dialog() as edit_note_dialog, ui.card():
                ui.label("Edit Note")

                edit_content = ui.textarea(
                    "Note",
                    value=note.content,
                )

                def save_note(note_id=note.id, field=edit_content):
                    if not field.value or not field.value.strip():
                        ui.notify(
                            "Note cannot be empty",
                            type="negative",
                        )
                        return

                    collab_manager.edit_task_note(
                        user=user,
                        task_id=task.id,
                        tnote_id=note_id,
                        content=field.value.strip(),
                    )

                    ui.notify("Note updated", type="positive")

                    edit_note_dialog.close()
                    ui.navigate.reload()

                ui.button("Save", on_click=save_note)

                ui.button(
                    "Cancel",
                    on_click=edit_note_dialog.close,
                )

            ui.button(
                "Edit Note",
                on_click=edit_note_dialog.open,
            )

            # DELETE NOTE
            def delete_note(note_id=note.id):
                collab_manager.delete_task_note(
                    user=user,
                    task_id=task.id,
                    tnote_id=note_id,
                )

                ui.notify("Note deleted", type="positive")

                ui.navigate.reload()

            ui.button(
                "Delete Note",
                on_click=delete_note,
            )

        # CREATE NOTE
        with ui.dialog() as add_note_dialog, ui.card():
            ui.label("New Task Note")

            content = ui.textarea("Note")

            def add_note():
                if not content.value or not content.value.strip():
                    ui.notify(
                        "Note cannot be empty",
                        type="negative",
                    )
                    return

                collab_manager.create_task_note(
                    user=user,
                    task_id=task.id,
                    content=content.value.strip(),
                )

                ui.notify("Note created", type="positive")

                add_note_dialog.close()
                ui.navigate.reload()

            ui.button("Create", on_click=add_note)

            ui.button(
                "Cancel",
                on_click=add_note_dialog.close,
            )

        ui.button(
            "Add Task Note",
            on_click=add_note_dialog.open,
        )


@ui.page("/task/{task_id}")
def task(task_id: int):

    session = db_conn.get_session()

    if not app_state.is_authenticated():
        ui.navigate.to("/")
        return

    user = app_state.get_current_user()

    task_manager = TaskManager()

    raw_task = session.query(Task).filter_by(
        id=task_id
    ).first()

    if raw_task is None:
        ui.label("Task not found")
        return

    project = raw_task.project

    loaded_task = task_manager.get_task_by_id(
        user=user,
        project=project,
        task_id=task_id,
    )

    if loaded_task is None:
        ui.label("Task not found")
        return

    TaskPage().render(loaded_task)
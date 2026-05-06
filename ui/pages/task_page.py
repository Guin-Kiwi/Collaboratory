"""
Task Page UI

Allows users to view, create, and edit tasks and task notes.
Uses TaskManager and CollabManager (no direct database access).
Route: /task/{task_id}
"""

from nicegui import ui

from ui.view import BaseView
from ui.layout import task_frame
from logic.app_state import app_state
from logic.task_manager import TaskManager
from logic.collab_manager import CollabManager
from database.models import Task


class TaskPage(BaseView):
    def render(self, task: Task) -> None:
        # Get current logged-in user and managers
        user = app_state.get_current_user()
        task_manager = TaskManager()
        collab_manager = CollabManager()

        # Render page layout
        task_frame(page=task.title, user=user, task=task)

        # Get project of this task
        project = task.project

        # Section: Task details
        ui.label("Task Details").classes("text-h6")

        # CREATE TASK
        with ui.dialog() as create_task_dialog, ui.card():
            ui.label("New Task")

            # Input fields for new task
            new_title = ui.input("Title")
            new_description = ui.textarea("Description")
            new_priority = ui.select(
                ["low", "medium", "high"],
                value="medium",
                label="Priority",
            )
            new_status = ui.select(
                ["todo", "in_progress", "completed"],
                value="todo",
                label="Status",
            )

            # Create new task
            def create_task():
                if not new_title.value.strip():
                    ui.notify("Title is required", type="negative")
                    return

                new_task = task_manager.create_task(
                    user=user,
                    project=project,
                    title=new_title.value.strip(),
                    description=new_description.value or "",
                    due_date=None,
                    priority=new_priority.value,
                    status=new_status.value,
                )

                ui.notify("Task created", type="positive")
                create_task_dialog.close()
                ui.navigate.to(f"/task/{new_task.id}")

            ui.button("Create", on_click=create_task)
            ui.button("Cancel", on_click=create_task_dialog.close)

        # Button to open create dialog
        ui.button("New Task", on_click=create_task_dialog.open)

        ui.separator()

        # EDIT TASK
        with ui.dialog() as edit_task_dialog, ui.card():
            ui.label("Edit Task")

            # Input fields for task update
            title = ui.input("Title", value=task.title)
            description = ui.textarea("Description", value=task.description or "")
            status = ui.select(
                ["todo", "in_progress", "completed"],
                value=task.status,
                label="Status",
            )

            # Save updated task
            def save_task():
                if not title.value.strip():
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

        # Button to open edit dialog
        ui.button("Edit Task", on_click=edit_task_dialog.open)

        ui.separator()

        # TASK NOTES
        ui.label("Task Notes").classes("text-h6")

        # Fetch notes for this task
        notes = collab_manager.view_task_note(user, task.id)

        for note in notes:
            ui.separator()
            ui.label(note.content)

            # EDIT NOTE
            with ui.dialog() as edit_note_dialog, ui.card():
                ui.label("Edit Note")
                edit_content = ui.textarea("Note", value=note.content)

                # Save updated note
                def save_note(note_id=note.id, field=edit_content):
                    if not field.value.strip():
                        ui.notify("Note cannot be empty", type="negative")
                        return

                    collab_manager.edit_task_note(
                        user=user,
                        task_id=task.id,
                        tnote_id=note_id,
                        content=field.value,
                    )

                    ui.notify("Note updated", type="positive")
                    edit_note_dialog.close()
                    ui.navigate.reload()

                ui.button("Save", on_click=save_note)
                ui.button("Cancel", on_click=edit_note_dialog.close)

            ui.button("Edit Note", on_click=edit_note_dialog.open)

            # DELETE NOTE
            def delete_note(note_id=note.id):
                collab_manager.delete_task_note(
                    user=user,
                    task_id=task.id,
                    tnote_id=note_id,
                )

                ui.notify("Note deleted", type="positive")
                ui.navigate.reload()

            ui.button("Delete Note", on_click=delete_note)

        # CREATE NOTE
        with ui.dialog() as add_note_dialog, ui.card():
            ui.label("New Task Note")
            content = ui.textarea("Note")

            # Create new note
            def add_note():
                if not content.value.strip():
                    ui.notify("Note cannot be empty", type="negative")
                    return

                collab_manager.create_task_note(
                    user=user,
                    task_id=task.id,
                    content=content.value,
                )

                ui.notify("Note created", type="positive")
                add_note_dialog.close()
                ui.navigate.reload()

            ui.button("Create", on_click=add_note)
            ui.button("Cancel", on_click=add_note_dialog.close)

        # Button to open note dialog
        ui.button("Add Task Note", on_click=add_note_dialog.open)


# ROUTE: Load task page by task ID
@ui.page("/task/{task_id}")
def task(task_id: int):
    # Get task manager and current user
    task_manager = TaskManager()
    user = app_state.get_current_user()

    # Redirect if not logged in
    if user is None:
        ui.navigate.to("/")
        return

    # Fetch task via logic layer
    task = task_manager.get_task_by_id(
        user=user,
        task_id=task.id,
    )

    # Handle missing task
    if task is None:
        ui.label("Task not found")
        return

    # Render task page
    TaskPage().render(task)

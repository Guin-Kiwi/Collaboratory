"""
Task Page UI

Allows users to view and edit tasks and manage task notes.
Route: /task/{task_id}
"""

from nicegui import ui

from logic.app_state import app_state
from logic.task_manager import TaskManager
from logic.collab_manager import CollabManager
from logic.permissions_manager import PermissionDenied
from database import db_conn
from database.models import Task, User
from ui.layout import TaskFrame


class TaskPage(TaskFrame):
    def __init__(self, user, task, session):
        super().__init__(user, task)

        self.user = user
        self.task = task
        self.session = session

    def render_content(self) -> None:
        with ui.column().classes("w-full h-full p-6 gap-6"):
            with ui.card().classes("w-full p-6 shadow-md"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label(self.task.title).classes("text-3xl font-bold")
                    ui.button("Manage Assignees", on_click=self.on_manage_assignees)

                ui.label(self.task.description or "No description").classes(
                    "text-lg text-grey-8 mt-2"
                )

                ui.separator()

                with ui.row().classes("gap-4 mt-2"):
                    ui.badge(
                        f"Status: {getattr(self.task, 'status', 'N/A')}",
                        color="blue",
                    )

                    ui.badge(
                        f"Priority: {getattr(self.task, 'priority', 'N/A')}",
                        color="orange",
                    )

                due_date = getattr(self.task, "due_date", None)

                if due_date:
                    ui.label(f"Due date: {due_date}").classes(
                        "text-sm text-grey-7 mt-2"
                    )

            with ui.card().classes("w-full p-6 shadow-md"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("Task Notes").classes("text-2xl font-bold")

                    with ui.row().classes("gap-2"):
                        ui.button("Manage Notes", on_click=self.on_manage_notes)
                        ui.button("Create Note", on_click=self.on_create_note)

                ui.label(
                    "Create, edit, or delete notes related to this task."
                ).classes("text-grey-7")

    def on_manage_assignees(self, e=None) -> None:
        tm = TaskManager(session=self.session)
        assignees = tm.get_assignees(self.user, self.task.id)

        with ui.dialog() as dlg, ui.card().classes("w-[450px]"):
            ui.label("Manage Assignees").classes("text-h6")

            if assignees:
                for assignee in assignees:
                    with ui.row().classes("items-center gap-4"):
                        ui.label(assignee.username)

                        ui.button(
                            "Remove",
                            on_click=lambda _, user_id=assignee.id: remove_user(user_id),
                        )

            else:
                ui.label("No assignees yet")

            ui.separator()

            users = self.session.query(User).all()
            options = {user.id: user.username for user in users}

            selected_user = ui.select(
                options=options,
                label="Select user",
            ).classes("w-full")

            def remove_user(user_id: int):
                tm.remove_assignee(self.user, self.task.id, user_id)
                dlg.close()
                ui.navigate.reload()

            def assign_user():
                if selected_user.value is None:
                    ui.notify("Please select a user", color="negative")
                    return

                tm.assign_task(
                    self.user,
                    self.task.project,
                    self.task.id,
                    selected_user.value,
                )

                dlg.close()
                ui.navigate.reload()

            with ui.row():
                ui.button("Assign", on_click=assign_user)
                ui.button("Close", on_click=dlg.close)

        dlg.open()

    def on_assign_user(self) -> None:
        self.on_manage_assignees()

    def on_create_note(self) -> None:
        self.on_manage_notes()

    def on_manage_notes(self, e=None) -> None:
        cm = CollabManager(session=self.session)

        try:
            notes = cm.view_task_note(self.user, self.task.id) or []

        except Exception as exc:
            ui.notify(f"Could not load notes: {exc}", color="negative")
            return

        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[640px]"):
            ui.label("Manage Task Notes").classes("text-h6")
            ui.label("Delete notes")

            checks = []

            if notes:
                with ui.column().classes("w-full gap-2"):
                    for note in notes:
                        with ui.row().classes("w-full items-center justify-between"):
                            with ui.column().classes("flex-1"):
                                ui.label(note.content).classes("text-sm")

                                if hasattr(note, "author") and note.author:
                                    ui.label(
                                        f"{note.author.username} • {note.created_at}"
                                    ).classes("text-xs text-grey")

                            cb = ui.checkbox()
                            checks.append((cb, note.id))

            else:
                ui.label("No notes available").classes("text-sm text-grey")

            def delete_selected(_=None):
                removed = 0

                for cb, note_id in checks:
                    if cb.value:
                        try:
                            ok = cm.delete_task_note(
                                user=self.user,
                                task_id=self.task.id,
                                tnote_id=note_id,
                            )

                            if ok:
                                removed += 1

                        except PermissionDenied:
                            ui.notify(
                                "You do not have permission to delete one or more selected notes",
                                color="negative",
                            )
                            return

                        except Exception as exc:
                            ui.notify(
                                f"Error deleting note: {exc}",
                                color="negative",
                            )
                            return

                if removed:
                    ui.notify(f"Removed {removed} note(s)", color="positive")
                    dlg.close()
                    ui.navigate.reload()

                else:
                    ui.notify("No notes selected", color="negative")

            if notes:
                with ui.row().classes("w-full justify-end"):
                    ui.button("Delete Selected", on_click=delete_selected)

            ui.separator()

            ui.label("Add a new note")

            content = ui.textarea("Note").props("autogrow").classes("w-full")

            def add_note(_=None):
                text = (content.value or "").strip()

                if not text:
                    ui.notify("Note cannot be empty", color="negative")
                    return

                try:
                    ok = cm.create_task_note(
                        user=self.user,
                        task_id=self.task.id,
                        content=text,
                    )

                    if ok:
                        ui.notify("Note created", color="positive")
                        dlg.close()
                        ui.navigate.reload()

                    else:
                        ui.notify("Could not create note", color="negative")

                except PermissionDenied:
                    ui.notify(
                        "You do not have permission to create notes",
                        color="negative",
                    )

                except Exception as exc:
                    ui.notify(f"Error creating note: {exc}", color="negative")

            with ui.row():
                ui.button("Create", on_click=add_note)
                ui.button("Cancel", on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_edit_note(self, note) -> None:
        cm = CollabManager(session=self.session)

        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[640px]"):
            ui.label("Edit Task Note").classes("text-h6")

            edit_content = ui.textarea(
                "Note",
                value=note.content,
            ).props("autogrow").classes("w-full")

            def save_note(_=None):
                text = (edit_content.value or "").strip()

                if not text:
                    ui.notify("Note cannot be empty", color="negative")
                    return

                try:
                    ok = cm.edit_task_note(
                        user=self.user,
                        task_id=self.task.id,
                        tnote_id=note.id,
                        content=text,
                    )

                    if ok:
                        ui.notify("Note updated", color="positive")
                        dlg.close()
                        ui.navigate.reload()

                    else:
                        ui.notify("Could not update note", color="negative")

                except PermissionDenied:
                    ui.notify(
                        "You do not have permission to edit this note",
                        color="negative",
                    )

                except Exception as exc:
                    ui.notify(f"Error editing note: {exc}", color="negative")

            with ui.row():
                ui.button("Save", on_click=save_note)
                ui.button("Cancel", on_click=lambda _=None: dlg.close())

        dlg.open()


@ui.page("/task/{task_id}")
def task(task_id: int) -> None:
    if not app_state.is_authenticated():
        ui.navigate.to("/")
        return

    user = app_state.get_current_user()

    session = db_conn.get_session()
    task_manager = TaskManager(session=session)

    raw_task = session.query(Task).filter_by(id=task_id).first()

    if raw_task is None:
        ui.notify("Task not found", color="negative")
        return

    try:
        loaded_task = task_manager.get_task_by_id(
            user=user,
            project=raw_task.project,
            task_id=task_id,
        )

    except PermissionDenied:
        ui.notify("Access denied", color="negative")
        return

    except Exception as exc:
        ui.notify(f"Error loading task: {exc}", color="negative")
        return

    if loaded_task is None:
        ui.notify("Task not found", color="negative")
        return

    TaskPage(user, loaded_task, session=session).render()
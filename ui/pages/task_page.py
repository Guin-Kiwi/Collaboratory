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
from logic.permissions_manager import check_permission, PermissionAction
from database.models import Task, User
from ui.layout import TaskFrame
from logic.user_manager import UserManager
from database import db_conn


class TaskPage(TaskFrame):
    def __init__(self, user, task, session=None):
        super().__init__(user, task, session=session)

    def on_manage_assignees(self, e=None) -> None:
        tm = TaskManager(session=self.session)
        assignees = tm.get_assignees(self.user, self.task.id)

        with ui.dialog() as dlg, ui.card().classes("w-[450px]"):
            ui.label("Manage Assignees").classes("text-h6")

            def remove_user(user_id: int):
                try:
                    ok = tm.remove_assignee(self.user, self.task.id, user_id)

                    if ok:
                        ui.notify("Assignee removed", color="positive")
                        dlg.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Could not remove assignee", color="negative")

                except PermissionDenied:
                    ui.notify(
                        "You do not have permission to remove this assignee",
                        color="negative",
                    )

                except Exception as exc:
                    ui.notify(f"Error removing assignee: {exc}", color="negative")

            if assignees:
                for assignee in assignees:
                    with ui.row().classes("items-center gap-4"):
                        if assignee:
                            ui.label(assignee.username)
                        else:
                            ui.label('Unknown')

                        can_remove = False
                        try:
                            can_remove = check_permission(self.user, PermissionAction.ASSIGN_TASK, self.session, project=self.project)
                        except Exception:
                            can_remove = False

                        if can_remove:
                            ui.button(
                                "Remove",
                                on_click=lambda _, user_id=assignee.id: remove_user(user_id),
                            )

            else:
                ui.label("No assignees yet")

            ui.separator()

            assigned_user_ids = [assignee.id for assignee in assignees]
            users = UserManager(session=self.session).get_all_users()

            options = {
                user.id: user.username
                for user in users
                if user.id not in assigned_user_ids
            }

            selected_user = ui.select(
                options=options,
                label="Select user",
            ).classes("w-full")

            def assign_user():
                if selected_user.value is None:
                    ui.notify("Please select a user", color="negative")
                    return

                project = tm.get_task_project(self.task.id)

                try:
                    ok = tm.assign_task(
                        self.user,
                        project,
                        self.task.id,
                        selected_user.value,
                    )

                    if ok:
                        ui.notify("User assigned to task", color="positive")
                        dlg.close()
                        ui.navigate.reload()

                    else:
                        ui.notify("Could not assign user to task", color="negative")

                except PermissionDenied:
                    ui.notify(
                        "You do not have permission to assign this task",
                        color="negative",
                    )

                except Exception as exc:
                    ui.notify(f"Error assigning task: {exc}", color="negative")

            with ui.row():
                ui.button("Assign", on_click=assign_user)
                ui.button("Close", on_click=dlg.close)

        dlg.open()

    def on_assign_user(self) -> None:
        self.on_manage_assignees()

    def on_create_note(self) -> None:
        cm = CollabManager(session=self.session)

        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[640px]"):
            ui.label("Create Task Note").classes("text-h6")

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

    def on_manage_notes(self, e=None) -> None:
        cm = CollabManager(session=self.session)

        try:
            notes = cm.view_task_note(self.user, self.task.id) or []

        except Exception as exc:
            ui.notify(f"Could not load notes: {exc}", color="negative")
            return

        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[640px]"):
            ui.label("Manage Task Notes").classes("text-h6")
            ui.label("Delete notes").classes("text-h7")

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

                            with ui.row().classes("gap-2"):
                                ui.button("Edit", on_click=lambda _, n=note: self.on_edit_note(n)).props("size=sm")
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

            with ui.row():
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

    def on_edit_status(self, e=None) -> None:
        tm = TaskManager(session=self.session)

        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[450px]"):
            ui.label("Change Task Status").classes("text-h6")

            status_select = ui.select(
                ["todo", "in_progress", "completed"],
                value=self.task.status,
                label="Status",
            ).classes("w-full")

            def save_status():
                try:
                    ok = tm.change_task_status(
                        user=self.user,
                        project=self.project,
                        task_id=self.task.id,
                        status=status_select.value,
                    )

                    if ok:
                        ui.notify("Task status updated", color="positive")
                        dlg.close()
                        ui.navigate.reload()

                    else:
                        ui.notify("Could not update task status", color="negative")

                except PermissionDenied:
                    ui.notify(
                        "You do not have permission to change this status",
                        color="negative",
                    )

                except Exception as exc:
                    ui.notify(f"Error changing status: {exc}", color="negative")

            with ui.row():
                ui.button("Save", on_click=save_status)
                ui.button("Cancel", on_click=dlg.close)

        dlg.open()

    def on_edit_task_details(self, e=None) -> None:
        tm = TaskManager(session=self.session)
        
        with ui.dialog().props("persistent") as dlg, ui.card().classes("w-[640px]"):
            ui.label("Edit Task Details").classes("text-h6")
            ui.separator()
            
            # Input fields
            title_input = ui.input(label="Task Title", value=self.task.title or "").classes("w-full")
            description_input = ui.textarea(label="Description", value=self.task.description or "").props("autogrow").classes("w-full")
            
            def save(_=None):
                title = (title_input.value or "").strip()
                description = (description_input.value or "").strip()
                
                if not title:
                    ui.notify("Task title cannot be empty", color="negative")
                    return
                
                try:
                    ok = tm.edit_task(
                        user=self.user,
                        project=self.project,
                        task_id=self.task.id,
                        title=title,
                        description=description
                    )
                    if ok:
                        ui.notify("Task details updated", color="positive")
                        dlg.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Could not update task details", color="negative")
                except PermissionDenied:
                    ui.notify("You do not have permission to edit this task", color="negative")
                except Exception as exc:
                    ui.notify(f"Error updating task: {exc}", color="negative")
            
            with ui.row():
                ui.button("Save", on_click=save)
                ui.button("Cancel", on_click=lambda _=None: dlg.close())
        
        dlg.open()

    def on_return_to_project(self, e=None) -> None:
        ui.navigate.to(f"/project/{self.project.id}")


@ui.page("/task/{task_id}")
def task(task_id: int) -> None:
    if not app_state.is_authenticated():
        ui.navigate.to("/")
        return

    user = app_state.get_current_user()
    session = db_conn.get_session()
    task_manager = TaskManager(session=session)

    try:
        loaded_task = task_manager.get_task_by_id(
            user=user,
            project=None,
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
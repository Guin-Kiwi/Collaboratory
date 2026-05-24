from datetime import datetime

from nicegui import ui, Client

from logic.app_state import app_state
from logic.collab_manager import CollabManager
from logic.task_manager import TaskManager
from logic.project_manager import ProjectManager
from logic.user_manager import UserManager
from logic.permissions_manager import PermissionDenied
from ui.layout import ProjectFrame
from database import db_conn


class ProjectPage(ProjectFrame):
    """Project detail page for authenticated users.

    Inherits from ProjectFrame which renders the header, right drawer
    with collaborators, and the two-column tasks/notes layout.
    This class implements all action methods for managing tasks,
    notes, collaborators, and project details.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cm = CollabManager(session=self.session)
        self.tm = TaskManager(session=self.session)
        self.pm = ProjectManager(session=self.session)
        self.um = UserManager(session=self.session)

    def on_create_note(self) -> None:
        """Open a dialog to create a new project note.

        Prompts the user for note content and calls CollabManager
        to persist it. Reloads the page on success.
        """
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Create Project Note').classes('text-h6')

            new_content = ui.textarea('Note').props('autogrow').classes('w-full')

            def add_note(_=None):
                """Validate and save the new note to the database."""
                text = (new_content.value or '').strip()
                if not text:
                    ui.notify('Note cannot be empty', color='negative')
                    return
                try:
                    ok = self.cm.create_project_note(user=self.user, project_id=self.project.id, content=text)
                    if ok:
                        ui.notify('Note created', color='positive')
                        dlg.close()
                        self._render_notes_card.refresh()
                    else:
                        ui.notify('Could not create note', color='negative')
                except PermissionDenied:
                    ui.notify('You do not have permission to create notes', color='negative')
                except Exception as exc:
                    ui.notify(f'Error creating note: {exc}', color='negative')

            with ui.row():
                ui.button('Create', on_click=add_note)
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_manage_tasks(self, e=None) -> None:
        """Open a dialog to create or delete tasks for this project.

        Shows existing tasks with checkboxes for bulk deletion, and
        a form to create new tasks with title, description, due date,
        priority, and status fields.
        """
        try:
            project = self.pm.view_project(self.user, self.project.id)
        except PermissionDenied:
            ui.notify('Access denied', color='negative')
            return
        if not project:
            ui.notify('Project not found', color='negative')
            return

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[720px]'):
            ui.label('Add or Remove Tasks').classes('text-h6')

            checks = []
            with ui.column().classes('w-full gap-2'):
                for t in project.tasks or []:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(t.title).classes('flex-1')
                        cb = ui.checkbox()
                        checks.append((cb, t.id))
                with ui.row().classes('w-full justify-end'):
                    def delete_selected_tasks(_=None):
                        """Delete all checked tasks from the project."""
                        removed = 0
                        for cb, task_id in checks:
                            if cb.value:
                                try:
                                    ok = self.tm.delete_task(user=self.user, project=project, task_id=task_id)
                                    if ok:
                                        removed += 1
                                    else:
                                        ui.notify('Could not delete one or more tasks', color='negative')
                                except PermissionDenied:
                                    ui.notify('You do not have permission to delete one or more selected tasks', color='negative')
                                    return
                                except Exception as exc:
                                    ui.notify(f'Error deleting task: {exc}', color='negative')
                                    return

                        if removed:
                            ui.notify(f'Removed {removed} task(s)', color='positive')
                            dlg.close()
                            self._render_tasks_card.refresh()
                            self._render_project_info.refresh()
                        else:
                            ui.notify('No tasks selected', color='negative')

                    ui.button('Delete Selected', on_click=delete_selected_tasks)

            ui.separator()
            ui.label('Create new task').classes('text-subtitle-1')

            title = ui.input('Title').classes('w-full')
            desc = ui.textarea('Description').classes('w-full')
            due = ui.input('Due date (YYYY-MM-DD) (optional)').classes('w-full')
            priority = ui.select(['low', 'medium', 'high'], value='medium').classes('w-36')
            status = ui.select(['todo', 'in_progress', 'completed'], value='todo').classes('w-48')

            def create_task(_=None):
                """Validate inputs and create a new task for this project."""
                t = (title.value or '').strip()
                if not t:
                    ui.notify('Title required', color='negative'); return
                due_date = None
                if due.value:
                    try:
                        due_date = datetime.fromisoformat(due.value).date()
                    except Exception:
                        ui.notify('Invalid date', color='negative'); return
                try:
                    new_task = self.tm.create_task(
                        user=self.user,
                        project=project,
                        title=t,
                        description=desc.value or '',
                        due_date=due_date,
                        priority=priority.value or 'medium',
                        status=status.value or 'todo',
                    )
                    ui.notify('Task created', color='positive')
                    dlg.close()
                    ui.navigate.to(f'/task/{new_task.id}')
                except PermissionDenied:
                    ui.notify('No permission to create task', color='negative')
                except Exception as exc:
                    ui.notify(f'Error: {exc}', color='negative')

            with ui.row():
                ui.button('Create', on_click=create_task)
                ui.button('Close', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_edit_note(self, note) -> None:
        """Open a dialog to edit an existing project note.

        Pre-fills the textarea with the current note content.
        Only the note author can edit their own notes.

        Args:
            note: The ProjectNote object to edit.
        """
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Edit Project Note').classes('text-h6')
            edit_content = ui.textarea('Note', value=note.content).props('autogrow')

            def save(_=None):
                """Validate and save the updated note content."""
                text = (edit_content.value or '').strip()
                if not text:
                    ui.notify('Note cannot be empty', color='negative')
                    return
                try:
                    ok = self.cm.edit_project_note(user=self.user, project_id=self.project.id, pnote_id=note.id, content=text)
                    if ok:
                        ui.notify('Note updated', color='positive')
                        dlg.close()
                        self._render_notes_card.refresh()
                    else:
                        ui.notify('Could not update note', color='negative')
                except PermissionDenied:
                    ui.notify('You do not have permission to edit this note', color='negative')
                except Exception as exc:
                    ui.notify(f'Error editing note: {exc}', color='negative')

            with ui.row():
                ui.button('Save', on_click=save)
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_delete_note(self, note) -> None:
        """Open a confirmation dialog before deleting a project note.

        Args:
            note: The ProjectNote object to delete.
        """
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Delete Note').classes('text-h6')
            ui.label('Are you sure you want to delete this note? This cannot be undone.').classes('text-sm')
            ui.label(f'"{note.content}"').classes('text-sm text-grey italic')

            def confirm(_=None):
                try:
                    ok = self.cm.delete_project_note(
                        user=self.user,
                        project_id=self.project.id,
                        pnote_id=note.id,
                    )
                    if ok:
                        ui.notify('Note deleted', color='positive')
                        dlg.close()
                        self._render_notes_card.refresh()
                    else:
                        ui.notify('Could not delete note', color='negative')
                except PermissionDenied:
                    ui.notify('You do not have permission to delete this note', color='negative')
                except Exception as exc:
                    ui.notify(f'Error: {exc}', color='negative')

            with ui.row():
                ui.button('Delete', on_click=confirm, color='red')
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_manage_collaborators(self, e=None) -> None:
        """Open a dialog to add or remove project collaborators.

        Shows existing collaborators with checkboxes for removal, and
        a dropdown to add new collaborators. Admins and the project owner
        are excluded from the add dropdown.
        """
        members = self.project.collaborator_memberships or []
        current_collaborator_ids = {membership.user.id for membership in members}

        all_users = sorted(self.um.get_all_users(), key=lambda u: u.name.lower())
        user_options = {
            user.id: f"{user.name} ({user.email})"
            for user in all_users
            if not user.is_admin
            and user.id != self.project.owner_id
            and user.id not in current_collaborator_ids
        }

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Manage Collaborators').classes('text-h6')
            ui.label("Collaborators get full visibility of this project and can create tasks, "
            "assign users, and write project notes. They cannot update task status or write"
            " task notes unless also assigned to a task.").classes('text-sm text-grey mb-4')
            ui.separator()
            ui.label('Remove collaborators').classes('text-h7')

            checks = []
            with ui.column().classes('w-full gap-2'):
                for membership in members:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(membership.user.name).classes('flex-1')
                        cb = ui.checkbox()
                        checks.append((cb, membership.user.id))

            def remove_selected(_=None):
                """Remove all checked collaborators from the project."""
                removed = 0
                for cb, user_id in checks:
                    if cb.value:
                        try:
                            ok = self.cm.remove_collaborator(
                                user=self.user,
                                project_id=self.project.id,
                                user_id=user_id,
                            )
                            if ok:
                                removed += 1
                            else:
                                ui.notify('Could not remove one or more collaborators', color='negative')
                        except PermissionDenied:
                            ui.notify('You do not have permission to remove collaborators', color='negative')
                            return
                        except Exception as exc:
                            ui.notify(f'Error removing collaborator: {exc}', color='negative')
                            return

                if removed:
                    ui.notify(f'Removed {removed} collaborator(s)', color='positive')
                    dlg.close()
                    self._render_collaborators_panel.refresh()
                else:
                    ui.notify('No collaborators selected', color='negative')

            with ui.row():
                ui.button('Remove Selected', on_click=remove_selected)

            ui.separator()
            ui.label('Add collaborators').classes('text-h5')
            username_select = ui.select(
                options=user_options,
                label='Username',
                with_input=True,
                clearable=True,
            ).classes('w-full')

            def add_collaborator(_=None):
                if not username_select.value:
                    ui.notify('Select a user', color='negative')
                    return

                try:
                    ok = self.cm.add_collaborator(
                        user=self.user,
                        project_id=self.project.id,
                        user_id=username_select.value,
                    )
                    if ok:
                        ui.notify('Collaborator added', color='positive')
                        dlg.close()
                        self._render_collaborators_panel.refresh()
                    else:
                        ui.notify('Could not add collaborator', color='negative')
                except PermissionDenied:
                    ui.notify('You do not have permission to add collaborators', color='negative')
                except Exception as exc:
                    ui.notify(f'Error adding collaborator: {exc}', color='negative')

            with ui.row():
                ui.button('Add', on_click=add_collaborator)
                ui.button('Cancel', on_click=lambda _: dlg.close())

        dlg.open()

    def on_manage_notes(self, e=None) -> None:
        """Open a dialog to delete project notes. Only accessible to owners."""
        try:
            notes = self.cm.view_project_note(self.user, self.project.id) or []
        except Exception as exc:
            ui.notify(f'Could not load notes: {exc}', color='negative')
            return

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Manage Project Notes').classes('text-h6')

            ui.label('Delete notes').classes('text-h7')
            checks: list[tuple] = []
            if notes:
                with ui.column().classes('w-full gap-2'):
                    for n in notes:
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('flex-1'):
                                ui.label(n.content).classes('text-sm')
                                ui.label(f'{n.author.name} • {n.created_at}').classes('text-xs text-grey')
                            with ui.row().classes('gap-2'):
                                cb = ui.checkbox()
                                checks.append((cb, n.id))
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Delete Selected', on_click=lambda _=None: delete_selected())
            else:
                ui.label('No notes available to delete').classes('text-sm text-grey')

            def delete_selected(_=None):
                """Delete all checked notes from the project."""
                removed = 0
                for cb, n_id in checks:
                    if cb.value:
                        try:
                            ok = self.cm.delete_project_note(user=self.user, project_id=self.project.id, pnote_id=n_id)
                            if ok:
                                removed += 1
                            else:
                                ui.notify('Could not delete one or more notes', color='negative')
                        except PermissionDenied:
                            ui.notify('You do not have permission to delete one or more selected notes', color='negative')
                            return
                        except Exception as exc:
                            ui.notify(f'Error deleting note: {exc}', color='negative')
                            return
                if removed:
                    ui.notify(f'Removed {removed} note(s)', color='positive')
                    dlg.close()
                    self._render_notes_card.refresh()
                else:
                    ui.notify('No notes selected', color='negative')

            with ui.row():
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_create_task(self) -> None:
        """Alias for on_manage_tasks."""
        self.on_manage_tasks()

    def on_add_collaborator(self) -> None:
        """Alias for on_manage_collaborators."""
        self.on_manage_collaborators()

    def on_edit_project_details(self, e=None) -> None:
        """Open a dialog to edit the project name and description.

        Only the project owner has permission to edit project details.
        Reloads the page on success.
        """
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Edit Project Details').classes('text-h6')
            ui.separator()

            name_input = ui.input(label='Project Name', value=self.project.name or '').classes('w-full')
            description_input = ui.textarea(label='Description', value=self.project.description or '').props('autogrow').classes('w-full')

            def save(_=None):
                """Validate and save the updated project name and description."""
                name = (name_input.value or '').strip()
                description = (description_input.value or '').strip()

                if not name:
                    ui.notify('Project name cannot be empty', color='negative')
                    return

                try:
                    ok = self.pm.edit_project_details(
                        user=self.user,
                        project_id=self.project.id,
                        name=name,
                        description=description
                    )
                    if ok:
                        ui.notify('Project details updated', color='positive')
                        dlg.close()
                        self._render_project_info.refresh()
                    else:
                        ui.notify('Could not update project details', color='negative')
                except PermissionDenied:
                    ui.notify('You do not have permission to edit this project', color='negative')
                except Exception as exc:
                    ui.notify(f'Error updating project: {exc}', color='negative')

            with ui.row():
                ui.button('Save', on_click=save)
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()


@ui.page('/project/{project_id}')
async def project(project_id: int, client: Client) -> None:
    """Register the project page at /project/{project_id} and render it.

    Redirects to login if the user is not authenticated. Loads the project
    via ProjectManager and passes it along with the current user and session
    to ProjectPage for rendering. The session is closed when the client disconnects.

    Args:
        project_id: The ID of the project to display, taken from the URL.
    """
    if not app_state.is_authenticated():
        ui.notify('Please log in to view projects', color='negative')
        ui.navigate.to('/login')
        return

    user = app_state.get_current_user()
    session = db_conn.get_session()
    try:
        try:
            project = ProjectManager(session=session).view_project(user, project_id)
        except PermissionDenied:
            ui.notify('Access denied', color='negative')
            return

        if not project:
            ui.notify('Project not found', color='negative')
            return

        ProjectPage(user, project, session=session).render()
        await client.disconnected()
    finally:
        session.close()
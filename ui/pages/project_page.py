# --- FOR UI DEVELOPERS ---
# To run the app locally:
#   1. Run: python main.py
#   2. Log in at http://localhost:8080, then navigate to a project.
#
# This page inherits ProjectFrame from ui/layout.py.
# Override these action methods:
#
#   def on_create_task(self) -> None:
#       called when "Create Task" is clicked in the left drawer
#
#   def on_add_collaborator(self) -> None:
#       called when "Add Collaborator" is clicked in the right drawer
#       owner only — CollabManager will raise PermissionDenied if not allowed
#
#   def on_create_note(self) -> None:
#       called when "Create Note" is clicked in the body
#
# Data available in your methods:
#   self.user     — the logged-in User object
#   self.project  — the current Project object
#
# Useful manager calls (CollabManager from logic/collab_manager.py):
#   manager.view_collaborators(user, project_id)
#   manager.add_collaborator(user, project_id, user_id)
#   manager.remove_collaborator(user, project_id, user_id)
#   manager.create_project_note(user, project_id, content)
#   manager.edit_project_note(user, project_id, pnote_id, content)
#   manager.delete_project_note(user, project_id, pnote_id)


from nicegui import ui

from logic.app_state import app_state       # route function: get_current_user()
from logic.collab_manager import CollabManager   # on_create_note(), on_add_collaborator()
from logic.task_manager import TaskManager       # on_create_task()
from logic.project_manager import ProjectManager
from logic.user_manager import UserManager       # on_add_collaborator(): find user by username
from logic.permissions_manager import PermissionDenied
from ui.layout import ProjectFrame
from database import db_conn

class ProjectPage(ProjectFrame):

    def on_create_task(self) -> None:
        self.on_manage_tasks()

    def on_add_collaborator(self) -> None:
        self.on_manage_collaborators()

    def on_create_note(self) -> None:
        cm = CollabManager(session=self.session)

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Create Project Note').classes('text-h6')

            new_content = ui.textarea('Note').props('autogrow').classes('w-full')

            def add_note(_=None):
                text = (new_content.value or '').strip()
                if not text:
                    ui.notify('Note cannot be empty', color='negative')
                    return
                try:
                    ok = cm.create_project_note(user=self.user, project_id=self.project.id, content=text)
                    if ok:
                        ui.notify('Note created', color='positive')
                        dlg.close()
                        ui.navigate.reload()
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
        tm = TaskManager(session=self.session)
        pm = ProjectManager(session=self.session)
        try:
            project = pm.view_project(self.user, self.project.id)
        except PermissionDenied:
            ui.notify('Access denied', color='negative')
            return
        if not project:
            ui.notify('Project not found', color='negative')
            return

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[720px]'):
            ui.label('Add or Remove Tasks').classes('text-h6')

            # Existing tasks: show as a selectable list with checkboxes and a
            # single "Delete Selected" action (no per-task Edit button here).
            checks = []
            with ui.column().classes('w-full gap-2'):
                for t in project.tasks or []:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(t.title).classes('flex-1')
                        cb = ui.checkbox()
                        checks.append((cb, t.id))
                with ui.row().classes('w-full justify-end'):
                    def delete_selected_tasks(_=None):
                        removed = 0
                        for cb, task_id in checks:
                            if cb.value:
                                try:
                                    ok = tm.delete_task(user=self.user, project=project, task_id=task_id)
                                    if ok:
                                        removed += 1
                                except PermissionDenied:
                                    ui.notify('You do not have permission to delete one or more selected tasks', color='negative')
                                    return
                                except Exception as exc:
                                    ui.notify(f'Error deleting task: {exc}', color='negative')
                                    return

                        if removed:
                            ui.notify(f'Removed {removed} task(s)', color='positive')
                            dlg.close()
                            ui.navigate.reload()
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
                t = (title.value or '').strip()
                if not t:
                    ui.notify('Title required', color='negative'); return
                due_date = None
                if due.value:
                    try:
                        from datetime import datetime
                        due_date = datetime.fromisoformat(due.value).date()
                    except Exception:
                        ui.notify('Invalid date', color='negative'); return
                try:
                    new_task = tm.create_task(
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

            def _open_edit(task):
                with ui.dialog().props('persistent') as ed, ui.card():
                    ui.label('Edit Task')
                    etitle = ui.input('Title', value=task.title)
                    edesc = ui.textarea('Description', value=task.description or '')
                    def save(_=None):
                        if not etitle.value.strip():
                            ui.notify('Title required', color='negative'); return
                        try:
                            ok = tm.update_task(
                                user=self.user,
                                project=project,
                                task_id=task.id,
                                title=etitle.value.strip(),
                                description=edesc.value or '',
                            )
                            if ok:
                                ui.notify('Task updated', color='positive')
                                ed.close()
                                dlg.close()
                                ui.navigate.reload()
                            else:
                                ui.notify('Could not update task', color='negative')
                        except PermissionDenied:
                            ui.notify('No permission to update task', color='negative')
                        except Exception as exc:
                            ui.notify(f'Error: {exc}', color='negative')
                    with ui.row():
                        ui.button('Save', on_click=save)
                        ui.button('Cancel', on_click=lambda _=None: ed.close())
                ed.open()

            def _delete_task(task):
                try:
                    ok = tm.delete_task(user=self.user, project=project, task_id=task.id)
                    if ok:
                        ui.notify('Task deleted', color='positive')
                        dlg.close()
                        ui.navigate.reload()
                    else:
                        ui.notify('Could not delete task', color='negative')
                except PermissionDenied:
                    ui.notify('No permission to delete task', color='negative')
                except Exception as exc:
                    ui.notify(f'Error deleting task: {exc}', color='negative')

            with ui.row():
                ui.button('Create', on_click=create_task)
                ui.button('Close', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_edit_note(self, note) -> None:
        cm = CollabManager(session=self.session)
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Edit Project Note').classes('text-h6')
            edit_content = ui.textarea('Note', value=note.content).props('autogrow')

            def save(_=None):
                text = (edit_content.value or '').strip()
                if not text:
                    ui.notify('Note cannot be empty', color='negative')
                    return
                try:
                    ok = cm.edit_project_note(user=self.user, project_id=self.project.id, pnote_id=note.id, content=text)
                    if ok:
                        ui.notify('Note updated', color='positive')
                        dlg.close()
                        ui.navigate.reload()
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

    def on_manage_collaborators(self, e=None) -> None:
        cm = CollabManager(session=self.session)
        um = UserManager(session=self.session)
        members = self.project.collaborator_memberships or []
        current_collaborator_ids = {membership.user.id for membership in members}

        all_users = um.get_all_users()
        user_options = {
            user.username: f'{user.username} - {user.name or ""}'
            for user in all_users
            if user.id != self.user.id and user.id not in current_collaborator_ids
            and not user.is_admin
        }

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Manage Collaborators').classes('text-h6')
            ui.separator()
            ui.label('Remove collaborators').classes('text-h7')

            checks = []
            with ui.column().classes('w-full gap-2'):
                for membership in members:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(membership.user.username).classes('flex-1')
                        cb = ui.checkbox()
                        checks.append((cb, membership.user.id))

            def remove_selected(_=None):
                removed = 0
                for cb, user_id in checks:
                    if cb.value:
                        try:
                            ok = cm.remove_collaborator(
                                user=self.user,
                                project_id=self.project.id,
                                user_id=user_id,
                            )
                            if ok:
                                removed += 1
                        except PermissionDenied:
                            ui.notify('You do not have permission to remove collaborators', color='negative')
                            return
                        except Exception as exc:
                            ui.notify(f'Error removing collaborator: {exc}', color='negative')
                            return

                if removed:
                    ui.notify(f'Removed {removed} collaborator(s)', color='positive')
                    dlg.close()
                    ui.navigate.reload()
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
                username = username_select.value
                if not username:
                    ui.notify('Select a username', color='negative')
                    return

                target_user = um.get_user_by_id(
                    next(
                        (user.id for user in all_users if user.username == username),
                        None,
                    )
                )
                if not target_user:
                    ui.notify('User not found', color='negative')
                    return

                try:
                    ok = cm.add_collaborator(
                        user=self.user,
                        project_id=self.project.id,
                        user_id=target_user.id,
                    )
                    if ok:
                        ui.notify('Collaborator added', color='positive')
                        dlg.close()
                        ui.navigate.reload()
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
        cm = CollabManager(session=self.session)
        try:
            notes = cm.view_project_note(self.user, self.project.id) or []
        except Exception as exc:
            ui.notify(f'Could not load notes: {exc}', color='negative')
            return

        # Determine which notes the current user may delete.
        # Users may delete their own notes; users with the DELETE_PROJECT_NOTE
        # permission (admins / owners / collaborators) may delete any.
        can_delete_any = cm.can_delete_project_note(self.user, self.project)

        deletable_notes = notes if can_delete_any else [n for n in notes if n.created_by == self.user.id]

        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Manage Project Notes').classes('text-h6')

            ui.label('Delete notes').classes('text-h7')
            checks: list[tuple] = []
            if deletable_notes:
                with ui.column().classes('w-full gap-2'):
                    for n in deletable_notes:
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('flex-1'):
                                ui.label(n.content).classes('text-sm')
                                ui.label(f'{n.author.username} • {n.created_at}').classes('text-xs text-grey')
                            with ui.row().classes('gap-2'):
                                ui.button('Edit', on_click=lambda _, note=n: self.on_edit_note(note)).props('size=sm')
                                cb = ui.checkbox()
                                checks.append((cb, n.id))
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Delete Selected', on_click=lambda _=None: delete_selected())
            else:
                ui.label('No notes available to delete').classes('text-sm text-grey')

            def delete_selected(_=None):
                removed = 0
                for cb, n_id in checks:
                    if cb.value:
                        try:
                            ok = cm.delete_project_note(user=self.user, project_id=self.project.id, pnote_id=n_id)
                            if ok:
                                removed += 1
                        except PermissionDenied:
                            ui.notify('You do not have permission to delete one or more selected notes', color='negative')
                            return
                        except Exception as exc:
                            ui.notify(f'Error deleting note: {exc}', color='negative')
                            return
                if removed:
                    ui.notify(f'Removed {removed} note(s)', color='positive')
                    dlg.close()
                    ui.navigate.reload()
                else:
                    ui.notify('No notes selected', color='negative')

            with ui.row():
                ui.button('Cancel', on_click=lambda _=None: dlg.close())

        dlg.open()

    def on_edit_project_details(self, e=None) -> None:
        pm = ProjectManager(session=self.session)
        
        with ui.dialog().props('persistent') as dlg, ui.card().classes('w-[640px]'):
            ui.label('Edit Project Details').classes('text-h6')
            ui.separator()
            
            # Input fields
            name_input = ui.input(label='Project Name', value=self.project.name or '').classes('w-full')
            description_input = ui.textarea(label='Description', value=self.project.description or '').props('autogrow').classes('w-full')
            
            def save(_=None):
                name = (name_input.value or '').strip()
                description = (description_input.value or '').strip()
                
                if not name:
                    ui.notify('Project name cannot be empty', color='negative')
                    return
                
                try:
                    ok = pm.edit_project(
                        user=self.user,
                        project=self.project,
                        name=name,
                        description=description
                    )
                    if ok:
                        ui.notify('Project details updated', color='positive')
                        dlg.close()
                        ui.navigate.reload()
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
def project(project_id: int) -> None:
    if not app_state.is_authenticated():
        ui.notify('Please log in to view projects', color='negative')
        ui.navigate.to('/login')
        return

    user = app_state.get_current_user()
    session = db_conn.get_session()

    try:
        project = ProjectManager(session=session).view_project(user, project_id)
    except PermissionDenied:
        ui.notify('Access denied', color='negative')
        return

    if not project:
        ui.notify('Project not found', color='negative')
        return

    ProjectPage(user, project, session=session).render()
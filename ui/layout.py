from abc import ABC, abstractmethod

from nicegui import ui
from database import db_conn
from database.models import User, Project, Task
from logic.app_state import app_state
from logic.project_manager import ProjectManager
from logic.collab_manager import CollabManager
from logic.user_manager import UserManager

class UnauthenticatedFrame(ABC):

    def render(self) -> None:
        if app_state.is_authenticated():
            ui.navigate.to('/dashboard')
            return

        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
            ui.label("Collaboratory").classes("text-3xl font-bold")
            ui.label('"where collaboration thrives"').classes("text-2xl italic")

        with ui.column().classes("w-full items-center mx-auto"):
            with ui.card().style('background-color: #d7e3f4').classes("items-center"):
                ui.label("Login or Sign Up").classes("font-bold text-2xl text-center")
                username_input = ui.input("Username").props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
                password_input = ui.input("Password", password=True).props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
                error_label = ui.label("").classes("text-red text-sm")

                with ui.row():
                    ui.button("Login", on_click=lambda: self.on_login(username_input.value, password_input.value, error_label))
                    ui.button("Sign Up", on_click=lambda: self.on_signup_open())
                ui.link("Forgot your password?", '#').on('click', lambda: self.on_forgot_open())

        self.render_content()

    @abstractmethod
    def on_login(self, username: str, password: str, error_label) -> None:
        """Handle login logic. Must be implemented by subclass."""
        pass

    @abstractmethod
    def on_signup_open(self) -> None:
        """Open signup dialog. Must be implemented by subclass."""
        pass

    def render_content(self) -> None:
        """Optional: override to render extra content like dialogs."""
        pass

    @abstractmethod
    def on_forgot_open(self) -> None:
        """Open forgot password dialog. Must be implemented by subclass."""
        pass


class AuthenticatedFrame(ABC):

    def __init__(self, user: User) -> None:
        self.user = user

    def on_logout(self) -> None:
        app_state.logout()
        ui.navigate.to('/')

    def on_dashboard(self) -> None:
        ui.navigate.to('/dashboard')

    def render(self) -> None:
        if not app_state.is_authenticated():
            ui.navigate.to('/')
            return
        self.render_content()

    @abstractmethod
    def render_content(self) -> None:
        """Build the page UI. Must be implemented by subclass."""
        pass


class NoteableFrame(AuthenticatedFrame):

    def render_header(self, title: str, right_drawer) -> None:
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            with ui.row():
                ui.button('Logout', on_click=self.on_logout)
                ui.button('Dashboard', on_click=self.on_dashboard)
            with ui.row():
                ui.label(title).classes('text-3xl')
                ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    def render_notes(self, notes) -> None:
        ui.button('Manage Notes', on_click=self.on_manage_notes)
        for note in notes:
            with ui.list().props('bordered separator').classes('w-full'):
                with ui.column().classes('w-full p-4'):
                    ui.label(note.content)
                    with ui.row().classes('w-full justify-between'):
                        ui.label(note.author.username).classes('text-sm text-grey')
                        ui.label(str(note.created_at)).classes('text-sm text-grey')
                    if self.user and getattr(note, 'created_by', None) == self.user.id:
                        ui.button('Edit', on_click=lambda _=None, n=note: self.on_edit_note(n)).classes('ml-2')
        with ui.page_sticky(x_offset=18, y_offset=18):
            ui.button('Create Note', on_click=self.on_create_note).props('fab')

    @abstractmethod
    def on_create_note(self) -> None:
        pass

    @abstractmethod
    def on_edit_note(self, note) -> None:
        pass

    @abstractmethod
    def render_content(self) -> None:
        pass


class DashboardFrame(AuthenticatedFrame):

    def __init__(self, user: User, session=None) -> None: 
        super().__init__(user) 
        self.session = session or db_conn.get_session() 

    @abstractmethod
    def on_create_project(self) -> None:
        pass

    @abstractmethod
    def on_delete_account(self) -> None:
        pass

    def on_manage_admins(self) -> None:
        um = UserManager(session=self.session)

        users = um.get_all_users()

        non_admin_users = {
            user.id: f"{user.username} - {user.name or ''}"
            for user in users
            if not user.is_admin
        }

        with ui.dialog().props("persistent") as dialog, ui.card().classes("w-[500px]"):
            ui.label("Promote User to Admin").classes("text-h6")

            if not non_admin_users:
                ui.label("There are no non-admin users to promote.").classes(
                    "text-sm text-grey"
                )
            else:
                selected_user = ui.select(
                    options=non_admin_users,
                    label="Select user",
                ).classes("w-full")

                def promote_user() -> None:
                    if selected_user.value is None:
                        ui.notify("Please select a user", color="negative")
                        return

                    ok = um.promote_user_to_admin(selected_user.value)

                    if ok:
                        ui.notify("User promoted to admin", color="positive")
                        dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("Could not promote user", color="negative")

                with ui.row():
                    ui.button("Promote", on_click=promote_user)
                    ui.button("Cancel", on_click=dialog.close)

        dialog.open()

    def render_content(self) -> None:
        pm = ProjectManager(session=self.session) 

        owned_projects = []
        collab_projects = []
        task_rows = []

        if self.user:
            owned_projects = pm.get_projects_by_owner(self.user.id)
            collab_projects = pm.get_projects_by_collaborator(self.user.id)
            owned_project_ids = {project.id for project in owned_projects}
            collab_projects = [
                project for project in collab_projects
                if project.id not in owned_project_ids
            ]

            all_projects = owned_projects + collab_projects

            for project in all_projects:
                tasks = pm.view_project_tasks(self.user, project.id)
                
                for task in tasks:
                    assigned_users = ", ".join(
                            assignment.user.username for assignment in task.assignments
                        )
                    task_rows.append({
                            "id": task.id,
                            "title": task.title,
                            "project": project.name,
                            "status": task.status,
                            "priority": task.priority,
                            "assigned_to": assigned_users if assigned_users else "-",
                        })


        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            with ui.column().classes("w-full gap-3 p-3"):
                ui.label("Actions").classes("text-xl font-bold")
                ui.button("Create New Project", on_click=self.on_create_project).classes("w-full")
                if self.user and self.user.is_admin:
                    ui.button("Manage Admins", on_click=self.on_manage_admins).classes("w-full")


        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
            with ui.row():
                ui.button('Logout', on_click=self.on_logout)
                ui.button('Delete Account', on_click=self.on_delete_account).props('color=negative flat')
            with ui.row():
                ui.label(f'Hello, {self.user.name}!').classes('text-3xl')
                ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

        with ui.column().classes('items-center mx-auto p-4'):
            ui.label('Welcome to Collaboratory!').classes('text-5xl font-bold')

            with ui.row().classes('w-full gap-4'):
                with ui.card().classes('p-4 shadow rounded'):
                    ui.label('Owned Projects').classes('text-xl font-bold mb-2')
                    if owned_projects:
                        for project in owned_projects:
                            ui.link(project.name, f'/project/{project.id}').classes('text-lg')
                    else:
                        ui.label('You do not own any projects yet.').classes('text-sm text-grey')

                with ui.card().classes('p-4 shadow rounded'):
                    ui.label('Collaborations').classes('text-xl font-bold mb-2')
                    if collab_projects:
                        for project in collab_projects:
                            ui.link(project.name, f'/project/{project.id}').classes('text-lg')
                    else:
                        ui.label('You are not collaborating on any projects yet.').classes('text-sm text-grey')
                
            ui.label('Task Overview').classes('text-2xl font-bold mt-8')

            columns = [
                {"name": "title", "label": "Task", "field": "title", "align": "left"},
                {"name": "project", "label": "Project", "field": "project", "align": "left"},
                {"name": "status", "label": "Status", "field": "status", "align": "left"},
                {"name": "priority", "label": "Priority", "field": "priority", "align": "left"},
                {"name": "assigned_to", "label": "Assigned To", "field": "assigned_to", "align": "left"},
            ]        

            ui.table(columns=columns, rows=task_rows).classes('w-full')

            
class ProjectFrame(NoteableFrame):

    def __init__(self, user: User, project: Project, session=None) -> None: 

        super().__init__(user) 
        self.project = project 
        self.session = session or db_conn.get_session() 

    @abstractmethod
    def on_create_task(self) -> None:
        pass

    @abstractmethod
    def on_add_collaborator(self) -> None:
        pass

    @abstractmethod
    def on_create_note(self) -> None:
        pass

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            cm = CollabManager(session=self.session)
            can_manage_collabs = cm.can_add_collaborator(self.user, self.project)
            if can_manage_collabs:
                ui.button('Manage Collaborators', on_click=self.on_manage_collaborators)
            ui.label('Collaborators')
            with ui.column().props('w-full bordered separator'):
                if self.project.collaborator_memberships:
                    for membership in self.project.collaborator_memberships:
                        with ui.card().classes('w-full p-2'):
                            with ui.row().classes('items-center justify-between'):
                                with ui.column():
                                    ui.label(membership.user.username).classes('font-bold')
                                    ui.label(membership.user.name).classes('text-sm text-grey')
                                    ui.link(membership.user.email, f'mailto:{membership.user.email}').classes('text-sm text-grey')

        self.render_header(self.project.name, right_drawer)

        with ui.column().classes("w-full h-full p-6 gap-6"):
            with ui.card().classes("w-full p-6 shadow-md"):
                ui.label(self.project.name).classes("text-3xl font-bold")

                ui.label(self.project.description or "No description").classes("text-lg text-grey-8 mt-2")

                ui.separator()

                task_count = len(self.project.tasks or [])

                with ui.row().classes("gap-4 mt-2"):
                    ui.badge(f"Project ID: {self.project.id}", color="blue")
                    ui.badge(f"Tasks: {task_count}", color="orange")
            try:
                notes = cm.view_project_note(self.user, self.project.id) or []
            except Exception:
                notes = []
            with ui.row().classes("w-full gap-6 items-start"):

                # LEFT COLUMN — Tasks
                with ui.card().classes("flex-1 p-6 shadow-md"):
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Project Tasks").classes("text-2xl font-bold")
                        ui.button("Add or Remove Tasks", on_click=self.on_manage_tasks)

                    if self.project.tasks:
                        with ui.column().classes("w-full gap-2 mt-3"):
                            for task in self.project.tasks:
                                with ui.row().classes(
                                    "w-full items-center justify-between p-3 rounded bg-blue-50"
                                ):
                                    with ui.column().classes("gap-0"):
                                        ui.link(task.title, f"/task/{task.id}").classes(
                                            "font-bold text-base"
                                        )
                                        ui.label(task.description or "No description").classes(
                                            "text-sm text-grey-7"
                                        )
                                    with ui.row().classes("gap-2"):
                                        ui.badge(task.status or "no status", color="blue")
                                        ui.badge(task.priority or "no priority", color="orange")
                    else:
                        ui.label("No tasks yet.").classes("text-sm text-grey-6 italic mt-2")

                # RIGHT COLUMN — Notes
                with ui.card().classes("flex-1 p-6 shadow-md"):
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Project Notes").classes("text-2xl font-bold")

                    #with ui.row().classes("gap-2"):
                        ui.button("Manage Notes", on_click=self.on_manage_notes)

                    ui.label("Create, edit, or delete notes related to this project.").classes("text-grey-7")

                    ui.separator()

                    if notes:
                        with ui.column().classes("w-full gap-2 mt-2"):
                            for note in notes:
                                with ui.card().classes("w-full p-3 bg-blue-50 shadow-sm"):
                                    ui.label(note.content).classes("text-sm")
                                    if hasattr(note, "author") and note.author:
                                        ui.label(
                                            f"{note.author.username} • {note.created_at}"
                                        ).classes("text-xs text-grey-6")
                    else:
                        ui.label("No notes yet.").classes("text-sm text-grey-6 italic")

class TaskFrame(NoteableFrame):

    def __init__(self, user: User, task: Task) -> None:
        super().__init__(user)
        self.task = task

    @abstractmethod
    def on_assign_user(self) -> None:
        pass

    @abstractmethod
    def on_create_note(self) -> None:
        pass

    @abstractmethod
    def on_manage_assignees(self, e=None) -> None:
        pass

    @abstractmethod
    def on_edit_status(self, e=None) -> None:
        pass

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            ui.label('Management').classes('font-bold text-lg mb-4')

            with ui.column().classes('w-full gap-4'):
                ui.label('Assignees').classes('font-bold')

                if self.task.assignments:
                    for assignment in self.task.assignments:
                        ui.label(f"• {assignment.user.username}")
                else:
                    ui.label('No assignees yet').classes('text-sm text-grey')

                ui.button('Manage Assignees', on_click=self.on_manage_assignees)
                ui.separator()
                ui.button('Edit Status', on_click=self.on_edit_status)

        self.render_header(self.task.title, right_drawer)

        with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-6'):
            with ui.card().classes('w-full p-6 shadow-md border-t-4 border-blue-500'):
                with ui.row().classes('w-full justify-between items-start'):
                    ui.label(self.task.title).classes('text-3xl font-bold text-blue-900')
                    ui.badge(self.task.status or 'No status', color='primary')

                ui.separator().classes('my-4')

                ui.label(self.task.description or 'No description').classes(
                    'text-lg text-grey-8'
                )

                with ui.row().classes('gap-4 mt-4'):
                    ui.badge(f"Priority: {self.task.priority or 'N/A'}", color='orange')

                    if self.task.due_date:
                        ui.badge(f"Due: {self.task.due_date}", color='blue')

            cm = CollabManager()

            try:
                notes = cm.view_task_note(self.user, self.task.id) or []
            except Exception:
                notes = []

            self.render_notes(notes)
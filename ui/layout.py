from abc import ABC, abstractmethod

from nicegui import ui
from database.models import User, Project, Task
from logic.app_state import app_state
from ui.view import BaseView
from logic.project_manager import ProjectManager
from logic.collab_manager import CollabManager


def public_frame(on_login, on_signup_open) -> None:
    """Helper to render the login form. Colleagues don't need to edit this."""
    with ui.column().classes("w-full items-center mx-auto"):
        with ui.card().style('background-color: #d7e3f4').classes("items-center"):
            ui.label("Login or Sign Up").classes("font-bold text-2xl text-center")
            username_input = ui.input("Username").props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            password_input = ui.input("Password", password=True).props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            error_label = ui.label("").classes("text-red text-sm")
            
            with ui.row():
                ui.button("Login", on_click=lambda: on_login(username_input.value, password_input.value, error_label))
                ui.button("Sign Up", on_click=on_signup_open)


## TO be removed
def task_frame(page, user, task) -> None:
    with ui.column().classes('w-full p-4 gap-2'):
        ui.label(page).classes('text-2xl font-bold')
        if user is not None:
            ui.label(f'Logged in as {user.username}').classes('text-sm text-grey')
        if task is not None and getattr(task, 'project', None) is not None:
            ui.label(f'Project: {task.project.name}').classes('text-sm text-grey')


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

    def __init__(self, user: User) -> None:
        super().__init__(user)

    @abstractmethod
    def on_create_project(self) -> None:
        pass

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            with ui.column().props('bordered separator'):
                ui.label('Tasks')
                if self.user and self.user.assignments:
                    for assignment in self.user.assignments:
                        ui.link(assignment.task.title, f'/task/{assignment.task.id}')

        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
            with ui.row():
                ui.button('Logout', on_click=self.on_logout)
            with ui.row():
                ui.label(f'Hello, {self.user.name}!').classes('text-3xl')
                ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

        with ui.left_drawer().style('background-color: #d7e3f4'):
            with ui.column().props('dense separator'):
                ui.button('Create Project', on_click=self.on_create_project)
                pm = ProjectManager()
                owned_projects = []
                collab_projects = []
                try:
                    if self.user:
                        owned_projects = pm.session.query(Project).filter_by(owner_id=self.user.id).all()
                        collab_projects = pm.get_projects_by_user(self.user.id)
                except Exception:
                    owned_projects = []
                    collab_projects = []

                ui.label('Owned Projects')
                if owned_projects:
                    for proj in owned_projects:
                        ui.link(proj.name, f'/project/{proj.id}')
                else:
                    ui.label('—').classes('text-sm text-grey')

                ui.label('Collaborations')
                if collab_projects:
                    for proj in collab_projects:
                        ui.link(proj.name, f'/project/{proj.id}')
                else:
                    ui.label('—').classes('text-sm text-grey')

        with ui.column().classes('items-center mx-auto p-4'):
            ui.label('Welcome to your dashboard!')

class ProjectFrame(NoteableFrame):

    def __init__(self, user: User, project: Project) -> None:
        super().__init__(user)
        self.project = project

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
            cm = CollabManager()
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

        with ui.left_drawer().style('background-color: #d7e3f4'):
            with ui.column().props('dense separator'):
                ui.button('Add or Remove Tasks', on_click=self.on_manage_tasks)
                ui.label('Tasks')
                if self.project.tasks:
                    for task in self.project.tasks:
                        ui.link(task.title, f'/task/{task.id}')

        with ui.column().classes('items-center mx-auto p-4'):
            ui.label(self.project.name)
            ui.label(self.project.description or '')
            cm = CollabManager()
            try:
                notes = cm.view_project_note(self.user, self.project.id) or []
            except Exception:
                notes = []
            self.render_notes(notes)

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

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            ui.button('Manage Assignees', on_click=self.on_manage_assignees)
            ui.label('Users Assigned to Tasks')
            with ui.column().props('bordered separator'):
                if self.task.assignments:
                    for assignment in self.task.assignments:
                        ui.label(assignment.user.username)

        self.render_header(self.task.title, right_drawer)

        with ui.left_drawer().style('background-color: #d7e3f4'):
            with ui.column().props('dense separator'):
                ui.label('Task details')
                ui.label(self.task.description or '')

        with ui.column().classes('items-center mx-auto p-4'):
            cm = CollabManager()
            try:
                notes = cm.view_task_note(self.user, self.task.id) or []
            except Exception:
                notes = []
            self.render_notes(notes)

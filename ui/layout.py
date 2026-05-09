from nicegui import ui
from database.models import User, Project, Task
from logic.app_state import app_state
from ui.view import BaseView

class AuthenticatedFrame(BaseView):

    def __init__(self, user: User) -> None:
        super().__init__()
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

    def render_content(self) -> None:
        raise NotImplementedError


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
        for note in notes:
            with ui.list().props('bordered separator').classes('w-full'):
                with ui.column().classes('w-full p-4'):
                    ui.label(note.content)
                    with ui.row().classes('w-full justify-between'):
                        ui.label(note.author.username).classes('text-sm text-grey')
                        ui.label(str(note.created_at)).classes('text-sm text-grey')
        ui.button('Create Note', on_click=self.on_create_note)

    def on_create_note(self) -> None:
        raise NotImplementedError

    def render_content(self) -> None:
        raise NotImplementedError


class DashboardFrame(AuthenticatedFrame):

    def __init__(self, user: User) -> None:
        super().__init__(user)

    def on_create_project(self) -> None:
        raise NotImplementedError

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
                ui.label('Projects')
                if self.user and self.user.owned_projects:
                    for proj in self.user.owned_projects:
                        ui.link(proj.name, f'/project/{proj.id}')

        with ui.column().classes('items-center mx-auto p-4'):
            ui.label('Welcome to your dashboard!')

class ProjectFrame(NoteableFrame):

    def __init__(self, user: User, project: Project) -> None:
        super().__init__(user)
        self.project = project

    def on_create_task(self) -> None:
        raise NotImplementedError

    def on_add_collaborator(self) -> None:
        raise NotImplementedError

    def on_create_note(self) -> None:
        raise NotImplementedError

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            ui.button('Add Collaborator', on_click=self.on_add_collaborator)
            ui.label('Collaborators')
            with ui.column().props('w-full bordered separator'):
                if self.project.collaborator_memberships:
                    for membership in self.project.collaborator_memberships:
                        with ui.card().classes('w-full p-2'):
                            ui.label(membership.user.username).classes('font-bold')
                            ui.label(membership.user.name).classes('text-sm text-grey')
                            ui.label(membership.user.email).classes('text-sm text-grey')

        self.render_header(self.project.name, right_drawer)

        with ui.left_drawer().style('background-color: #d7e3f4'):
            with ui.column().props('dense separator'):
                ui.button('Create Task', on_click=self.on_create_task)
                ui.label('Tasks')
                if self.project.tasks:
                    for task in self.project.tasks:
                        ui.link(task.title, f'/task/{task.id}')

        with ui.column().classes('items-center mx-auto p-4'):
            ui.label(self.project.name)
            ui.label(self.project.description or '')
            self.render_notes(self.project.notes)

class TaskFrame(NoteableFrame):

    def __init__(self, user: User, task: Task) -> None:
        super().__init__(user)
        self.task = task

    def on_assign_user(self) -> None:
        raise NotImplementedError

    def on_create_note(self) -> None:
        raise NotImplementedError

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            ui.button('Assign User to Task', on_click=self.on_assign_user)
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
            self.render_notes(self.task.notes)

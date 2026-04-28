from nicegui import ui 

from database.models import User, Task, Project, Assignment


def public_frame() -> None:
    with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
        ui.label("Collaboratory").classes("text-3xl")
        ui.label('"where collaboration thrives"').classes("text-2xl italic")
    with ui.column().classes("w-full items-center mx-auto"):
        with ui.card().style('background-color: #d7e3f4').classes("items-center"):
            ui.label("Login or Sign Up").classes("font-bold text-2xl text-center")
            ui.input("Username").props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            ui.input("Password", password = True).props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            ui.button("Login")
            ui.button("Sign Up")


def project_frame(page: str, user: User, project: Project) -> None:
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.Button('Collaboratory').mark('important')
        ui.header(page).style
        ui.button('Logout')
        ui.button('Dashboard')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    with ui.left_drawer().style('background-color: #d7e3f4'):
        with ui.column().props('dense separator'):
            ui.label('Tasks')
            if project and project.tasks:
                for task in project.tasks:
                    ui.link(f"{task.title}", f"/{task.id}")

    with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
        with ui.column().props('bordered separator'):
            ui.label('Projects')
            if user and user.owned_projects:
                for proj in user.owned_projects:
                    ui.link(f"{proj.title}", f"/{proj.id}")

def dashboard_frame(page: str, user: User,) -> None:
    """A frame for the user's main dashboard page."""
    ui.query('.nicegui-content').classes('w-full')
    with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
        with ui.column().props('bordered separator'):
            ui.label('Tasks')
            if user and user.assignments:
                for assignment in user.assignments:
                    task = assignment.task
                    ui.link(f"{task.title}", f"/{task.id}")

    with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
        ui.button('Logout')
        ui.label("User Dashboard").classes("text-3xl")
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')                        

    with ui.left_drawer().style('background-color: #d7e3f4'):
        with ui.column().props('dense separator'):
            ui.button("Create Project")
            ui.label('Projects')
            with ui.column().props('bordered separator'):
                if user and user.owned_projects:
                    for proj in user.owned_projects:
                        ui.link(f"{proj.name}", f"/{proj.id}")

    with ui.column().classes("items-center mx-auto p-4"):
        ui.label("Welcome to your dashboard!")
        ui.label("Your Task notes")
        if user and user.assignments:
            for assignment in user.assignments:
                task = assignment.task
                for note in task.notes:
                    if note.author == user:
                        with ui.list().props('bordered separator').classes('w-full'):
                            with ui.item():
                                ui.label(f"{note.content}")
                                ui.label(f"{note.created_at}")





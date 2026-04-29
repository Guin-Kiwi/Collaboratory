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
    with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
        ui.label("Collaborators")
        with ui.column().props('w-full bordered separator'):
            if project and project.collaborator_memberships:
                for membership in project.collaborator_memberships:
                    with ui.card().classes('w-full p-2'):
                        ui.label(membership.user.username).classes('font-bold')
                        ui.label(membership.user.name).classes('text-sm text-grey')
                        ui.label(membership.user.email).classes('text-sm text-grey')

    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button('Logout')
        ui.button('Dashboard')
        ui.label(f"{project.name}").classes('text-3xl')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    with ui.left_drawer().style('background-color: #d7e3f4'):
        with ui.column().props('dense separator'):
            ui.label('Tasks')
            if project and project.tasks:
                for task in project.tasks:
                    ui.link(f"{task.title}", f"/{task.id}")

    with ui.column().classes("items-center mx-auto p-4"):
        ui.label(f"{project.name} notes")
        ui.label(f"{project.description}")
        if project and project.notes:
            for note in project.notes:
                with ui.list().props('bordered separator').classes('w-full'):
                    with ui.column().classes('w-full p-4'):
                        ui.label(f"{note.content}")
                        with ui.row().classes('w-full justify-between'):
                            ui.label(f"{note.author.username}").classes('text-sm text-grey')
                            ui.label(f"{note.created_at}").classes('text-sm text-grey')

def task_frame(page: str, user: User, task: Task) -> None:
    with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
        ui.label("Users Assigned to Tasks")
        with ui.column().props('bordered separator'):
            if task and task.assignments:
                for assignment in task.assignments:
                    ui.label(assignment.user.username)


    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.button('Logout')
        ui.button('Dashboard')
        ui.label(f"{task.title}").classes('text-3xl')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    with ui.left_drawer().style('background-color: #d7e3f4'):
        with ui.column().props('dense separator'):
            ui.label('Task details')
            ui.label(f"{task.description}")
            

    with ui.column().classes("items-center mx-auto p-4"):
        if task and task.notes:
            ui.label(f"{task.title} notes") 
            for note in task.notes:
                with ui.list().props('bordered separator').classes('w-full'):
                    with ui.item():
                        ui.label(f"{note.content}")
                        ui.label(f"{note.author.username}")
                        ui.label(f"{note.created_at}")

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





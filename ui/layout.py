from nicegui import ui 

from database.models import User, Task, Project, Assignment


def public_frame() -> None:
    with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
        ui.label("Collaboratory").classes("text-3xl")
        ui.label('"where collaboration thrives"').classes("text-2xl text-italic")
    with ui.column().classes("w-full items-center mx-auto q-gutter-md"):
        with ui.card().style('background-color: #d7e3f4').classes("items-center"):
            ui.label("Login or Sign Up").classes("font-bold text-2xl text-center")
            ui.input("Username").props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            ui.input("Password", password = True).props('bordered').classes('border border-solid border-gray-400 rounded justify-center').style("background-color: #FFFFFF")
            ui.button("Login").style("hover:background-color: #3874c8")
            ui.button("Sign Up").style("hover:background-color: #3874c8")


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


@ui.page('/dashboard')
def test():
    public_frame(user=None, project=None)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0')
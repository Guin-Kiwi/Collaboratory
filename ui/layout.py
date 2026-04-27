from nicegui import ui 

from database.models import User, Task, Project, Assignment


def frame(page: str, user: User, project: Project) -> None :
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


@ui.page('/')
def test():
    frame('Dashboard', user=None, project=None)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0')
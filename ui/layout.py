from abc import ABC, abstractmethod

from nicegui import ui
from database import db_conn
from database.models import User, Project, Task
from logic.app_state import app_state
from logic.project_manager import ProjectManager
from logic.collab_manager import CollabManager
from logic.user_manager import UserManager
from logic.task_manager import TaskManager
from logic.permissions_manager import check_permission, PermissionAction


class UnauthenticatedFrame(ABC):
    """Abstract base frame for pages accessible without authentication.

    Renders the public header and login form. Subclasses must implement
    on_login(), on_signup_open(), and on_forgot_open() to handle user
    interactions. render_content() can optionally be overridden to inject
    additional content such as dialogs below the form.
    """

    def render(self) -> None:
        """Render the public header and login form.

        Redirects to /dashboard if the user is already authenticated.
        Calls render_content() at the end to allow subclasses to inject
        additional UI elements such as signup or forgot password dialogs.
        """
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
        """Handle login form submission. Must be implemented by subclass."""
        pass

    @abstractmethod
    def on_signup_open(self) -> None:
        """Open the signup dialog. Must be implemented by subclass."""
        pass

    def render_content(self) -> None:
        """Optional hook for subclasses to render extra content such as dialogs."""
        pass

    @abstractmethod
    def on_forgot_open(self) -> None:
        """Open the forgot password dialog. Must be implemented by subclass."""
        pass


class AuthenticatedFrame(ABC):
    """Abstract base frame for pages that require authentication.

    Redirects to the login page if the user is not authenticated.
    Provides shared navigation helpers on_logout() and on_dashboard().
    Subclasses must implement render_content() to build the page UI.

    Attributes:
        user: The currently authenticated User object.
    """

    def __init__(self, user: User) -> None:
        """Initialise the frame with the currently authenticated user.

        Args:
            user: The logged-in User object.
        """
        self.user = user

    def on_logout(self) -> None:
        """Log the current user out and redirect to the login page."""
        app_state.logout()
        ui.navigate.to('/')

    def on_dashboard(self) -> None:
        """Navigate to the dashboard page."""
        ui.navigate.to('/dashboard')

    def render(self) -> None:
        """Render the page, redirecting to login if not authenticated."""
        if not app_state.is_authenticated():
            ui.navigate.to('/')
            return
        self.render_content()

    @abstractmethod
    def render_content(self) -> None:
        """Build the page UI. Must be implemented by subclass."""
        pass


class NoteableFrame(AuthenticatedFrame):
    """Abstract base frame for pages that display notes.

    Extends AuthenticatedFrame with shared header and note rendering
    helpers. Used by ProjectFrame and TaskFrame. Subclasses must
    implement on_create_note(), on_edit_note(), and render_content().
    """

    def render_header(self, title: str, right_drawer, extra_buttons=None) -> None:
        """Render the shared page header with navigation buttons and a drawer toggle.

        Args:
            title: The page title displayed in the header.
            right_drawer: The NiceGUI drawer element to toggle on menu click.
            extra_buttons: Optional list of (label, callback) buttons to add after Dashboard.
        """
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            with ui.row():
                ui.button('Logout', on_click=self.on_logout)
                ui.button('Dashboard', on_click=self.on_dashboard)

                if extra_buttons:
                    for label, callback in extra_buttons:
                        ui.button(label, on_click=callback)

            with ui.row():
                ui.label(title).classes('text-3xl')
                ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

    def render_notes(self, notes) -> None:
        """Render a list of notes with an Add/Remove Notes button and a scroll-to-top button.

        Args:
            notes: List of note objects to display. Each note must have
                   content, author, and created_at attributes.
        """
        with ui.row().classes('w-full items-center gap-2'):
            ui.label('Notes').classes('text-lg font-bold')
            ui.button('Add or Remove Notes', on_click=self.on_manage_notes).classes('text-sm')

        if notes:
            with ui.column().classes('w-full gap-2 mt-2'):
                for note in notes:
                    with ui.card().classes('w-full p-3 bg-blue-50 shadow-sm'):
                        ui.label(note.content).classes('text-sm')
                        if hasattr(note, 'author') and note.author:
                            ui.label(f"{note.author.username} • {note.created_at}").classes('text-xs text-grey-6')
        else:
            ui.label('No notes yet.').classes('text-sm text-grey-6 italic mt-2')

        with ui.page_sticky(x_offset=18, y_offset=18):
            ui.button(
                icon='arrow_upward',
                on_click=lambda: ui.run_javascript("window.scrollTo({top:0, behavior:'smooth'})"),
            ).props('fab')

    @abstractmethod
    def on_create_note(self) -> None:
        """Open a dialog to create a new note. Must be implemented by subclass."""
        pass

    @abstractmethod
    def on_edit_note(self, note) -> None:
        """Open a dialog to edit an existing note. Must be implemented by subclass.

        Args:
            note: The note object to edit.
        """
        pass

    @abstractmethod
    def render_content(self) -> None:
        """Build the page UI. Must be implemented by subclass."""
        pass


class DashboardFrame(AuthenticatedFrame):
    """Abstract base frame for the dashboard page.

    Renders the full dashboard layout including the header, right drawer
    with actions, owned projects, collaborations, and a task overview table.
    Subclasses must implement on_create_project() and on_delete_account().

    Attributes:
        session: The active SQLAlchemy database session.
    """

    def __init__(self, user: User, session=None) -> None:
        """Initialise the dashboard frame with a user and optional session.

        Args:
            user: The logged-in User object.
            session: Optional SQLAlchemy session. Falls back to shared db_conn session.
        """
        super().__init__(user)
        self.session = session or db_conn.get_session()

    @abstractmethod
    def on_create_project(self) -> None:
        """Open a dialog to create a new project. Must be implemented by subclass."""
        pass

    @abstractmethod
    def on_delete_account(self) -> None:
        """Open a dialog to delete the current user's account. Must be implemented by subclass."""
        pass

    def on_manage_admins(self) -> None:
        """Open a dialog to promote users to admin or revoke admin status."""
        um = UserManager(session=self.session)

        users = um.get_all_users()

        non_admin_users = {
            user.id: f"{user.username} - {user.name or ''}"
            for user in users
            if not user.is_admin
        }

        admin_users = {
            user.id: f"{user.username} - {user.name or ''}"
            for user in users
            if user.is_admin and user.id != self.user.id
        }

        with ui.dialog().props("persistent") as dialog, ui.card().classes("w-[500px]"):
            ui.label("Promote User to Admin").classes("text-h6")

            if not non_admin_users:
                ui.label("There are no non-admin users to promote.").classes("text-sm text-grey")
            else:
                selected_user = ui.select(
                    options=non_admin_users,
                    label="Select user",
                ).classes("w-full")

                def promote_user() -> None:
                    """Promote the selected user to admin status."""
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

                ui.button("Promote", on_click=promote_user)

                ui.separator()

                ui.label("Revoke Admin Status").classes("text-h6")

                if not admin_users:
                    ui.label("There are no other admins to revoke.").classes("text-sm text-grey")
                else:
                    selected_admin = ui.select(
                        options=admin_users,
                        label="Select admin",
                    ).classes("w-full")

                    def revoke_admin() -> None:
                        """Revoke admin status from the selected admin user."""
                        if selected_admin.value is None:
                            ui.notify("Please select an admin", color="negative")
                            return

                        ok = um.revoke_admin_status(selected_admin.value)

                        if ok:
                            ui.notify("Admin status revoked", color="positive")
                            dialog.close()
                            ui.navigate.reload()
                        else:
                            ui.notify("Could not revoke admin status", color="negative")

                    with ui.row():
                        ui.button("Revoke", on_click=revoke_admin, color="red")
                ui.separator()

                with ui.row().classes("w-full justify-end"):
                    ui.button("Cancel", on_click=dialog.close)

            dialog.open()

    def on_manage_projects(self) -> None:
        """Open a dialog to delete owned projects."""
        pm = ProjectManager(session=self.session)

        owned_projects = pm.get_projects_by_owner(self.user.id)

        with ui.dialog().props("persistent") as dialog, ui.card().classes("w-[650px]"):
            ui.label("Manage Projects").classes("text-h6")

            if not owned_projects:
                ui.label("You do not own any projects yet.").classes("text-sm text-grey")
            else:
                for project in owned_projects:
                    collaborator_count = len(project.collaborator_memberships or [])

                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label(project.name).classes("font-bold")
                            ui.label(
                                f"{collaborator_count} collaborator(s)"
                            ).classes("text-sm text-grey")

                        def delete_project(project_id=project.id):
                            """Delete the project and reload the dashboard."""
                            try:
                                ok = pm.delete_project(
                                    user=self.user,
                                    project_id=project_id,
                                )

                                if ok:
                                    ui.notify("Project deleted", color="positive")
                                    dialog.close()
                                    ui.navigate.reload()
                                else:
                                    ui.notify("Could not delete project", color="negative")

                            except Exception as exc:
                                ui.notify(f"Error deleting project: {exc}", color="negative")

                        ui.button(
                            "Delete",
                            on_click=delete_project,
                            color="red",
                        )

            with ui.row().classes("w-full justify-end"):
                ui.button("Close", on_click=dialog.close)

        dialog.open()

    def render_content(self) -> None:
        """Render the full dashboard layout."""
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
                ui.button("Manage Projects", on_click=self.on_manage_projects).classes("w-full")
                if self.user and self.user.is_admin:
                    ui.button("Manage Admins", on_click=self.on_manage_admins).classes("w-full")

        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between'):
            with ui.row():
                with ui.button(icon='more_vert').props('flat color=white'):
                    with ui.menu():
                        ui.menu_item(
                            'Delete Account',
                            self.on_delete_account,
                        ).classes('text-red')
                ui.button('Logout', on_click=self.on_logout)
            with ui.row():
                ui.label(f'Hello, {self.user.name}!').classes('text-3xl')
                ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

        with ui.column().classes("w-full p-6 gap-6"):

            with ui.card().classes("w-full p-6 shadow-md"):
                ui.label("Welcome to Collaboratory!").classes("text-3xl font-bold")
                ui.label(
                    "Manage your projects, collaborations, and assigned tasks."
                ).classes("text-lg text-grey-8 mt-2")
                ui.separator()

                with ui.row().classes("gap-4 mt-2"):
                    ui.badge(f"Owned Projects: {len(owned_projects)}", color="blue")
                    ui.badge(f"Collaborations: {len(collab_projects)}", color="orange")
                    ui.badge(f"Tasks: {len(task_rows)}", color="green")

            ui.separator()

            with ui.row().classes("w-full gap-6 items-start no-wrap"):

                with ui.card().classes("w-1/3 p-6 shadow-md"):
                    ui.label("Owned Projects").classes("text-2xl font-bold mb-6")

                    if owned_projects:
                        for project in owned_projects:
                            with ui.card().classes("w-full bg-blue-50 p-4 mb-3 shadow-sm"):
                                ui.link(
                                    project.name,
                                    f"/project/{project.id}"
                                ).classes("text-blue-700 underline text-lg")

                with ui.card().classes("w-1/3 p-6 shadow-md"):
                    ui.label("Collaborations").classes("text-2xl font-bold mb-6")

                    if collab_projects:
                        for project in collab_projects:
                            with ui.card().classes("w-full bg-blue-50 p-4 mb-3 shadow-sm"):
                                ui.link(
                                    project.name,
                                    f"/project/{project.id}"
                                ).classes("text-blue-700 underline text-lg")

                with ui.card().classes("w-1/3 p-6 shadow-md"):
                    ui.label("My Tasks").classes("text-2xl font-bold mb-6")

                    if task_rows:
                        for task in task_rows:
                            with ui.card().classes("w-full bg-blue-50 p-4 mb-3 shadow-sm"):
                                ui.link(
                                    task["title"],
                                    f"/task/{task['id']}"
                                ).classes("text-blue-700 underline text-lg")

            ui.separator()

            ui.label("Task Overview").classes("text-2xl font-bold mt-8")

            columns = [
                {"name": "title", "label": "Task", "field": "title", "align": "left"},
                {"name": "project", "label": "Project", "field": "project", "align": "left"},
                {"name": "status", "label": "Status", "field": "status", "align": "left"},
                {"name": "priority", "label": "Priority", "field": "priority", "align": "left"},
                {"name": "assigned_to", "label": "Assigned To", "field": "assigned_to", "align": "left"},
            ]

            if task_rows:
                ui.table(columns=columns, rows=task_rows).classes("w-full")
            else:
                with ui.card().classes("w-full p-4 shadow-sm"):
                    ui.label("You do not have any tasks yet.").classes("text-sm text-grey-6 italic")


class ProjectFrame(NoteableFrame):
    """Abstract base frame for the project detail page."""

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

    @abstractmethod
    def on_edit_project_details(self) -> None:
        pass

    @abstractmethod
    def on_manage_tasks(self) -> None:
        pass

    @abstractmethod
    def on_manage_collaborators(self) -> None:
        pass

    @abstractmethod
    def on_manage_notes(self) -> None:
        pass

    @abstractmethod
    def on_edit_note(self, note) -> None:
        pass

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            with ui.column().classes('w-full p-4 gap-4'):
                cm = CollabManager(session=self.session)
                can_manage_collabs = cm.can_add_collaborator(self.user, self.project)

                if can_manage_collabs:
                    ui.button(
                        'Manage Collaborators',
                        on_click=self.on_manage_collaborators
                    ).classes('w-full')

                with ui.column().classes('gap-2'):
                    ui.label('Project Owner').classes('font-bold text-lg')

                    with ui.card().classes('w-full p-3 shadow-sm').style('background-color: #fff4e6'):
                        ui.label(self.project.owner.username).classes('font-bold')
                        ui.label(self.project.owner.name).classes('text-sm text-grey')
                        ui.link(
                            self.project.owner.email,
                            f'mailto:{self.project.owner.email}'
                        ).classes('text-sm text-grey')

                with ui.column().classes('gap-2'):
                    ui.label('Collaborators').classes('font-bold text-lg')

                    if self.project.collaborator_memberships:
                        for membership in self.project.collaborator_memberships:
                            with ui.card().classes('w-full p-3 shadow-sm'):
                                ui.label(membership.user.username).classes('font-bold')
                                ui.label(membership.user.name).classes('text-sm text-grey')

                                ui.link(
                                    membership.user.email,
                                    f'mailto:{membership.user.email}'
                                ).classes('text-sm text-grey')

        self.render_header(self.project.name, right_drawer)

        with ui.column().classes("w-full h-full p-6 gap-6"):
            with ui.card().classes("w-full p-6 shadow-md relative"):
                ui.label(self.project.name).classes("text-3xl font-bold")
                ui.label(self.project.description or "No description").classes("text-lg text-grey-8 mt-2")
                ui.separator()

                task_count = len(self.project.tasks or [])

                with ui.row().classes("gap-4 mt-2 flex-wrap"):
                    ui.badge(f"Project ID: {self.project.id}", color="blue")
                    ui.badge(f"Tasks: {task_count}", color="orange")

                    can_edit_project = check_permission(
                        self.user,
                        PermissionAction.EDIT_PROJECT_DETAILS,
                        self.session,
                        project=self.project,
                    )
                    if can_edit_project:
                        ui.button('Edit Project Details', on_click=self.on_edit_project_details).classes('absolute top-4 right-4')

            with ui.grid(columns='1fr 1fr').classes('w-full gap-4'):
                with ui.card().classes('w-full p-6 shadow-md relative'):
                    with ui.row().classes('w-full gap-4 items-start'):
                        ui.label('Project Tasks').classes('text-2xl font-bold')
                        ui.button('Add or Remove Tasks', on_click=self.on_manage_tasks).classes('absolute top-4 right-4')

                    if self.project.tasks:
                        with ui.column().classes('w-full gap-2 mt-3'):
                            for task in self.project.tasks:
                                with ui.row().classes(
                                    'w-full items-center justify-between p-3 rounded bg-blue-50'
                                ):
                                    with ui.column().classes('gap-0'):
                                        ui.link(task.title, f'/task/{task.id}').classes('font-bold text-base')
                                        ui.label(task.description or 'No description').classes('text-sm text-grey-7')

                                    with ui.row().classes('gap-2'):
                                        ui.badge(task.status or 'no status', color='blue')
                                        ui.badge(task.priority or 'no priority', color='orange')
                    else:
                        ui.label('No tasks yet.').classes('text-sm text-grey-6 italic mt-2')

                with ui.card().classes('w-full p-6 shadow-md'):
                    ui.label('Project Notes').classes('text-2xl font-bold')

                    with ui.row().classes('gap-2'):
                        can_create_note = check_permission(
                            self.user,
                            PermissionAction.WRITE_PROJECT_NOTE,
                            self.session,
                            project=self.project,
                        )
                        if can_create_note:
                            ui.button('Create Note', on_click=self.on_create_note).props('size=sm')

                        can_manage_notes = check_permission(
                            self.user,
                            PermissionAction.DELETE_PROJECT_NOTE,
                            self.session,
                            project=self.project,
                        )
                        if can_manage_notes:
                            ui.button('Manage Notes', on_click=self.on_manage_notes).props('size=sm')

                    ui.label('Create, edit, or delete notes related to this project.').classes('text-grey-7')

                    try:
                        notes = cm.view_project_note(self.user, self.project.id) or []
                    except Exception:
                        notes = []

                    ui.separator()

                    if notes:
                        with ui.column().classes('w-full gap-2 mt-2'):
                            for note in notes:
                                with ui.card().classes('w-full p-3 bg-blue-50 shadow-sm'):
                                    with ui.row().classes('w-full items-start justify-between'):
                                        with ui.column().classes('flex-1'):
                                            ui.label(note.content).classes('text-sm')
                                            if hasattr(note, 'author') and note.author:
                                                ui.label(
                                                    f"{note.author.username} • {note.created_at}"
                                                ).classes('text-xs text-grey-6')

                                        if note.created_by == self.user.id:
                                            ui.button('Edit', on_click=lambda _, n=note: self.on_edit_note(n)).props('size=sm')
                    else:
                        ui.label('No notes yet.').classes('text-sm text-grey-6 italic')


class TaskFrame(NoteableFrame):
    """Abstract base frame for the task detail page."""

    def __init__(self, user: User, task: Task, session=None) -> None:
        super().__init__(user)
        self.task = task
        self.session = session or db_conn.get_session()
        self.project = self.session.query(Project).filter_by(id=getattr(task, 'project_id', None)).first()

    @abstractmethod
    def on_assign_user(self) -> None:
        pass

    @abstractmethod
    def on_create_note(self) -> None:
        pass

    @abstractmethod
    def on_manage_notes(self) -> None:
        pass

    @abstractmethod
    def on_manage_assignees(self, e=None) -> None:
        pass

    @abstractmethod
    def on_edit_status(self, e=None) -> None:
        pass

    @abstractmethod
    def on_edit_task_details(self, e=None) -> None:
        pass

    @abstractmethod
    def on_return_to_project(self) -> None:
        pass

    @abstractmethod
    def on_edit_note(self, note) -> None:
        pass

    def render_content(self) -> None:
        with ui.right_drawer().style('background-color: #ebf1fa') as right_drawer:
            ui.label('Management').classes('font-bold text-lg mb-4')
            can_manage_assignees = check_permission(
                self.user,
                PermissionAction.ASSIGN_TASK,
                self.session,
                project=self.project,
                task=self.task,
            )
            if can_manage_assignees:
                ui.button('Manage Assignees', on_click=self.on_manage_assignees)
            ui.label('Assignees').classes('font-bold')
            with ui.column().props('w-full bordered separator'):
                if self.task.assignments:
                    for assignment in self.task.assignments:
                        with ui.card().classes('w-full p-2'):
                            with ui.row().classes('items-center justify-between'):
                                with ui.column():
                                    ui.label(assignment.user.username).classes('font-bold')
                                    ui.label(assignment.user.name).classes('text-sm text-grey')
                                    ui.link(
                                        assignment.user.email,
                                        f'mailto:{assignment.user.email}'
                                    ).classes('text-sm text-grey')
                else:
                    ui.label('No assignees yet').classes('text-sm text-grey')

        self.render_header(
            self.task.title,
            right_drawer,
            extra_buttons=[('Return to Project', self.on_return_to_project)]
        )

        with ui.grid(columns='1fr 1fr').classes('w-full gap-4'):
            with ui.card().classes('w-full p-6 shadow-md relative'):
                with ui.row().classes('w-full items-center gap-4'):
                    ui.label(self.task.title).classes('text-3xl font-bold text-blue-900')

                    can_change_status = check_permission(
                        self.user,
                        PermissionAction.CHANGE_TASK_STATUS,
                        self.session,
                        project=self.project,
                        task=self.task,
                    )
                    if can_change_status:
                        ui.button('Edit Status', on_click=self.on_edit_status).classes('absolute top-4 right-4')

                    can_edit_details = check_permission(
                        self.user,
                        PermissionAction.EDIT_TASK_DETAILS,
                        self.session,
                        project=self.project,
                        task=self.task,
                    )
                    if can_edit_details:
                        ui.button('Edit Task Details', on_click=self.on_edit_task_details).classes('absolute top-4 right-4')

                ui.separator().classes('my-4')

                ui.label(self.task.description or 'No description').classes('text-lg text-grey-8')

                with ui.row().classes('gap-4 mt-4 flex-wrap'):
                    ui.badge(self.task.status or 'No status', color='primary')
                    ui.badge(f"Priority: {self.task.priority or 'N/A'}", color='orange')

                    if self.task.due_date:
                        ui.badge(f"Due: {self.task.due_date}", color='blue')

            with ui.card().classes('w-full p-6 shadow-md relative'):
                with ui.row().classes('w-full items-center gap-4'):
                    ui.label('Task Notes').classes('text-2xl font-bold')

                    can_create_note = check_permission(
                        self.user,
                        PermissionAction.WRITE_TASK_NOTE,
                        self.session,
                        project=self.project,
                        task=self.task,
                    )
                    if can_create_note:
                        ui.button('Create Note', on_click=self.on_create_note).props('size=sm')

                    can_manage_notes = check_permission(
                        self.user,
                        PermissionAction.DELETE_TASK_NOTE,
                        self.session,
                        project=self.project,
                        task=self.task,
                    )
                    if can_manage_notes:
                        ui.button('Manage Notes', on_click=self.on_manage_notes).classes('absolute top-4 right-4')

                ui.label('Create, edit, or delete notes related to this task.').classes('text-grey-7')

                try:
                    cm = CollabManager(session=self.session)
                    notes = cm.view_task_note(self.user, self.task.id) or []
                except Exception:
                    notes = []

                ui.separator()

                if notes:
                    with ui.column().classes('w-full gap-2 mt-2'):
                        for note in notes:
                            with ui.card().classes('w-full p-3 bg-blue-50 shadow-sm'):
                                with ui.row().classes('w-full items-start justify-between'):
                                    with ui.column().classes('flex-1'):
                                        ui.label(note.content).classes('text-sm')
                                        if hasattr(note, 'author') and note.author:
                                            ui.label(
                                                f"{note.author.username} • {note.created_at}"
                                            ).classes('text-xs text-grey-6')

                                    if note.created_by == self.user.id:
                                        ui.button('Edit', on_click=lambda _, n=note: self.on_edit_note(n)).props('size=sm')
                else:
                    ui.label('No notes yet.').classes('text-sm text-grey-6 italic')
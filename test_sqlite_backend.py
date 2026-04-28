"""Quick SQLite backend smoke test for the Collaboratory ORM models.

What this script does:
1) Wipes and recreates the main database file
2) Creates tables from SQLAlchemy ORM models
3) Inserts sample Users, Projects, Tasks, Assignments, ProjectMembers, and Notes
4) Reads everything back and prints transparent step-by-step logs

Run:
    python test_sqlite_backend.py
"""

from __future__ import annotations

from pathlib import Path
import datetime
import logging

from database.connection import DatabaseConnection
from database.models import Assignment, Project, Task, User
from database.collab_models import ProjectMember, ProjectNote, TaskNote


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
log = logging.getLogger("sqlite-test")


def reset_database_file(db_file: Path) -> None:
    if db_file.exists():
        log.info("Removing old database: %s", db_file)
        db_file.unlink()


def seed_data(db: DatabaseConnection) -> None:
    """Insert sample rows across all entities with transparent logs."""
    with db.get_session() as session:

        # --- Users ---
        log.info("Creating sample users")
        users = [
            User(username="alice", name="Alice Nguyen",  email="alice@example.com",  password="pw_alice",  is_admin=True),
            User(username="bob",   name="Bob Okafor",    email="bob@example.com",    password="pw_bob"),
            User(username="carol", name="Carol Petrov",  email="carol@example.com",  password="pw_carol"),
            User(username="dan",   name="Dan Kwesi",     email="dan@example.com",    password="pw_dan"),
        ]
        session.add_all(users)
        session.flush()
        for u in users:
            log.info("Inserted User(id=%s, username=%s)", u.id, u.username)

        # --- Projects ---
        log.info("Creating sample projects")
        projects = [
            Project(name="Website Revamp",     description="Refresh the company landing page",       owner_id=users[0].id),
            Project(name="Analytics Pipeline", description="Track product usage metrics",             owner_id=users[1].id),
            Project(name="Mobile App v2",      description="Second version of the iOS/Android app",  owner_id=users[0].id),
        ]
        session.add_all(projects)
        session.flush()
        for p in projects:
            log.info("Inserted Project(id=%s, name=%s, owner=%s)", p.id, p.name, p.owner_id)

        # --- Tasks ---
        log.info("Creating sample tasks")
        tasks = [
            Task(title="Draft wireframes",          description="Prepare 3 homepage layout options",      status="todo",        priority="high",   due_date=datetime.datetime.now() + datetime.timedelta(days=7),  project_id=projects[0].id, created_by=users[0].id),
            Task(title="Write copy for About page", description="500 words, friendly tone",               status="in_progress", priority="medium", due_date=datetime.datetime.now() + datetime.timedelta(days=5),  project_id=projects[0].id, created_by=users[0].id),
            Task(title="Write QA checklist",        description="Regression checklist before deployment", status="completed",   priority="low",    due_date=datetime.datetime.now() + datetime.timedelta(days=3),  project_id=projects[0].id, created_by=users[2].id),
            Task(title="Implement tracking events", description="Capture button clicks and page views",   status="in_progress", priority="medium", due_date=datetime.datetime.now() + datetime.timedelta(days=14), project_id=projects[1].id, created_by=users[1].id),
            Task(title="Set up data warehouse",     description="Configure BigQuery tables",              status="todo",        priority="high",   due_date=datetime.datetime.now() + datetime.timedelta(days=10), project_id=projects[1].id, created_by=users[1].id),
            Task(title="Fix login crash on iOS",    description="Crash on login with special chars",      status="todo",        priority="high",   due_date=datetime.datetime.now() + datetime.timedelta(days=2),  project_id=projects[2].id, created_by=users[0].id),
            Task(title="Add dark mode",             description="Support system dark mode preference",    status="todo",        priority="medium", due_date=datetime.datetime.now() + datetime.timedelta(days=20), project_id=projects[2].id, created_by=users[0].id),
        ]
        session.add_all(tasks)
        session.flush()
        for t in tasks:
            log.info("Inserted Task(id=%s, title=%s, status=%s, project_id=%s)", t.id, t.title, t.status, t.project_id)

        # --- Assignments ---
        log.info("Creating sample assignments")
        assignments = [
            Assignment(task_id=tasks[0].id, user_id=users[1].id),
            Assignment(task_id=tasks[0].id, user_id=users[2].id),
            Assignment(task_id=tasks[1].id, user_id=users[2].id),
            Assignment(task_id=tasks[3].id, user_id=users[0].id),
            Assignment(task_id=tasks[4].id, user_id=users[3].id),
            Assignment(task_id=tasks[5].id, user_id=users[3].id),
        ]
        session.add_all(assignments)
        session.flush()
        for a in assignments:
            log.info("Inserted Assignment(task_id=%s, user_id=%s)", a.task_id, a.user_id)

        # --- Project Members (collaborators) ---
        log.info("Creating sample project members")
        members = [
            ProjectMember(project_id=projects[0].id, user_id=users[1].id),
            ProjectMember(project_id=projects[0].id, user_id=users[2].id),
            ProjectMember(project_id=projects[1].id, user_id=users[3].id),
            ProjectMember(project_id=projects[2].id, user_id=users[1].id),
            ProjectMember(project_id=projects[2].id, user_id=users[3].id),
        ]
        session.add_all(members)
        session.flush()
        for m in members:
            log.info("Inserted ProjectMember(project_id=%s, user_id=%s)", m.project_id, m.user_id)

        # --- Project Notes ---
        log.info("Creating sample project notes")
        project_notes = [
            ProjectNote(content="Kickoff meeting notes: align on brand colours before wireframes.", project_id=projects[0].id, created_by=users[0].id),
            ProjectNote(content="Client approved the new navigation structure.",                    project_id=projects[0].id, created_by=users[1].id),
            ProjectNote(content="BigQuery quota increase request submitted to ops.",                project_id=projects[1].id, created_by=users[1].id),
            ProjectNote(content="Decided to drop Android support for v2 launch.",                  project_id=projects[2].id, created_by=users[0].id),
        ]
        session.add_all(project_notes)
        session.flush()
        for n in project_notes:
            log.info("Inserted ProjectNote(id=%s, project_id=%s)", n.id, n.project_id)

        # --- Task Notes ---
        log.info("Creating sample task notes")
        task_notes = [
            TaskNote(content="Started with mobile layout first — looks cleaner.",       task_id=tasks[0].id, created_by=users[1].id),
            TaskNote(content="Second round of feedback from design — minor tweaks.",    task_id=tasks[0].id, created_by=users[2].id),
            TaskNote(content="Copy draft sent to client for review.",                   task_id=tasks[1].id, created_by=users[2].id),
            TaskNote(content="Tracking events firing correctly in staging.",             task_id=tasks[3].id, created_by=users[0].id),
            TaskNote(content="Reproduced the crash — special chars in email field.",    task_id=tasks[5].id, created_by=users[3].id),
        ]
        session.add_all(task_notes)
        session.flush()
        for n in task_notes:
            log.info("Inserted TaskNote(id=%s, task_id=%s)", n.id, n.task_id)

        session.commit()
        log.info("Seed data committed")


def read_back_data(db: DatabaseConnection) -> None:
    """Read and print all data to verify stored rows and relationships."""
    with db.get_session() as session:

        log.info("--- Users ---")
        for u in session.query(User).order_by(User.id).all():
            log.info("User -> id=%s username=%s name=%s admin=%s", u.id, u.username, u.name, u.is_admin)

        log.info("--- Projects ---")
        for p in session.query(Project).order_by(Project.id).all():
            log.info("Project -> id=%s name=%s owner=%s", p.id, p.name, p.owner.username)

        log.info("--- Tasks ---")
        for t in session.query(Task).order_by(Task.id).all():
            log.info("Task -> id=%s title=%s status=%s priority=%s project=%s creator=%s",
                     t.id, t.title, t.status, t.priority, t.project.name, t.creator.username)

        log.info("--- Assignments ---")
        for a in session.query(Assignment).order_by(Assignment.id).all():
            log.info("Assignment -> task=%s assignee=%s", a.task.title, a.user.username)

        log.info("--- Project Members (collaborators) ---")
        for m in session.query(ProjectMember).order_by(ProjectMember.id).all():
            log.info("ProjectMember -> project=%s collaborator=%s", m.project.name, m.user.username)

        log.info("--- Project Notes ---")
        for n in session.query(ProjectNote).order_by(ProjectNote.id).all():
            log.info("ProjectNote -> project=%s author=%s content=%s", n.project.name, n.author.username, n.content)

        log.info("--- Task Notes ---")
        for n in session.query(TaskNote).order_by(TaskNote.id).all():
            log.info("TaskNote -> task=%s author=%s content=%s", n.task.title, n.author.username, n.content)


def main() -> None:
    db_path = Path(__file__).resolve().parent / "database" / "tracker_app.db"
    log.info("Seeding main app database")
    log.info("Target DB path: %s", db_path)

    reset_database_file(db_path)

    db = DatabaseConnection(db_path=str(db_path))
    db.init()
    log.info("Database initialised and tables created")

    seed_data(db)
    read_back_data(db)

    db.dispose()
    log.info("Done. Database connection disposed")


if __name__ == "__main__":
    main()

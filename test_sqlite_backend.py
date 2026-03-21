"""Quick SQLite backend smoke test for the Collaboratory ORM models.

What this script does:
1) Creates a fresh SQLite database file in database/test_tracker_app.db
2) Creates tables from SQLAlchemy ORM models
3) Inserts sample Users, Projects, Tasks, and Assignments
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


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
log = logging.getLogger("sqlite-test")


def reset_database_file(db_file: Path) -> None:
    """Ensure test runs start from a clean SQLite file."""
    if db_file.exists():
        log.info("Removing old test database: %s", db_file)
        db_file.unlink()


def seed_data(db: DatabaseConnection) -> None:
    """Insert sample rows across all entities with transparent logs."""
    with db.get_session() as session:
        log.info("Creating sample users")
        users = [
            User(
                username="alice",
                email="alice@example.com",
                password="hashed_pw_alice",
            ),
            User(
                username="bob",
                email="bob@example.com",
                password="hashed_pw_bob",
            ),
            User(
                username="carol",
                email="carol@example.com",
                password="hashed_pw_carol",
            ),
        ]
        session.add_all(users)
        session.flush()
        for u in users:
            log.info("Inserted User(id=%s, username=%s)", u.id, u.username)

        log.info("Creating sample projects")
        projects = [
            Project(
                name="Website Revamp",
                description="Refresh company landing page",
                owner_id=users[0].id,
            ),
            Project(
                name="Analytics Pipeline",
                description="Track product usage metrics",
                owner_id=users[1].id,
            ),
        ]
        session.add_all(projects)
        session.flush()
        for p in projects:
            log.info("Inserted Project(id=%s, name=%s, owner_id=%s)", p.id, p.name, p.owner_id)

        log.info("Creating sample tasks")
        tasks = [
            Task(
                title="Draft wireframes",
                description="Prepare 3 homepage layout options",
                status="todo",
                priority="high",
                due_date=datetime.datetime.now() + datetime.timedelta(days=7),
                project_id=projects[0].id,
                created_by=users[0].id,
            ),
            Task(
                title="Implement tracking events",
                description="Capture button clicks and page views",
                status="in_progress",
                priority="medium",
                due_date=datetime.datetime.now() + datetime.timedelta(days=14),
                project_id=projects[1].id,
                created_by=users[1].id,
            ),
            Task(
                title="Write QA checklist",
                description="Regression checklist before deployment",
                status="done",
                priority="low",
                due_date=datetime.datetime.now() + datetime.timedelta(days=3),
                project_id=projects[0].id,
                created_by=users[2].id,
            ),
        ]
        session.add_all(tasks)
        session.flush()
        for t in tasks:
            log.info(
                "Inserted Task(id=%s, title=%s, status=%s, project_id=%s)",
                t.id,
                t.title,
                t.status,
                t.project_id,
            )

        log.info("Creating sample assignments")
        assignments = [
            Assignment(task_id=tasks[0].id, user_id=users[1].id),
            Assignment(task_id=tasks[0].id, user_id=users[2].id),
            Assignment(task_id=tasks[1].id, user_id=users[0].id),
        ]
        session.add_all(assignments)
        session.flush()
        for a in assignments:
            log.info("Inserted Assignment(id=%s, task_id=%s, user_id=%s)", a.id, a.task_id, a.user_id)

        session.commit()
        log.info("Seed data committed")


def read_back_data(db: DatabaseConnection) -> None:
    """Read and print data to demonstrate stored rows and relationships."""
    with db.get_session() as session:
        log.info("Reading users")
        users = session.query(User).order_by(User.id).all()
        for u in users:
            log.info("User -> id=%s username=%s email=%s", u.id, u.username, u.email)

        log.info("Reading projects with owner usernames")
        projects = session.query(Project).order_by(Project.id).all()
        for p in projects:
            owner_name = p.owner.username if p.owner else "<none>"
            log.info("Project -> id=%s name=%s owner=%s", p.id, p.name, owner_name)

        log.info("Reading tasks with project and creator")
        tasks = session.query(Task).order_by(Task.id).all()
        for t in tasks:
            project_name = t.project.name if t.project else "<none>"
            creator_name = t.creator.username if t.creator else "<none>"
            log.info(
                "Task -> id=%s title=%s status=%s project=%s creator=%s",
                t.id,
                t.title,
                t.status,
                project_name,
                creator_name,
            )

        log.info("Reading assignments with task title and assignee username")
        assignments = session.query(Assignment).order_by(Assignment.id).all()
        for a in assignments:
            task_title = a.task.title if a.task else "<none>"
            username = a.user.username if a.user else "<none>"
            log.info(
                "Assignment -> id=%s task=%s assignee=%s assigned_at=%s",
                a.id,
                task_title,
                username,
                a.assigned_at,
            )


def main() -> None:
    db_path = Path(__file__).resolve().parent / "database" / "test_tracker_app.db"
    log.info("Starting SQLite smoke test")
    log.info("Target DB path: %s", db_path)

    reset_database_file(db_path)

    db = DatabaseConnection(db_path=str(db_path))
    db.init()
    log.info("Database initialized and tables created")

    seed_data(db)
    read_back_data(db)

    db.dispose()
    log.info("Done. Database connection disposed")


if __name__ == "__main__":
    main()

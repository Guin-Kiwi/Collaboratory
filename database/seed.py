"""Database seeding helpers.

We insert sample users, projects, tasks, and notes on first start.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path so imports work when running directly
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bcrypt
import datetime
from sqlalchemy.orm import Session

from database.models import User, Project, Task, Assignment
from database.collab_models import ProjectMember, ProjectNote, TaskNote


class DatabaseSeeder:
    """Seeds the database with sample data for development and testing."""

    def seed(self, session: Session) -> None:
        """Insert sample data only if the database is empty."""
        if session.query(User).first():
            return 
        """Insert sample users, projects, tasks, assignments, and notes."""

        def hash_pw(password: str) -> str:
            return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # --- Users ---
        users = [
            User(username="admin", name="Admin User", email="admin@example.com", password=hash_pw("admin"), is_admin=True),
            User(username="bob",   name="Bob Okafor", email="bob@example.com",   password=hash_pw("bob"),   is_admin=False),
            User(username="carol", name="Carol Petrov", email="carol@example.com", password=hash_pw("carol"), is_admin=False),
            User(username="dan",   name="Dan Kwesi",  email="dan@example.com",   password=hash_pw("dan"),   is_admin=False),
        ]
        for u in users:
            session.add(u)
        session.flush()

        # --- Projects ---
        projects = [
            Project(name="Website Revamp",     description="Refresh the company landing page",      owner_id=users[0].id),
            Project(name="Analytics Pipeline", description="Track product usage metrics",            owner_id=users[1].id),
            Project(name="Mobile App v2",      description="Second version of the iOS/Android app", owner_id=users[0].id),
        ]
        for p in projects:
            session.add(p)
        session.flush()

        # --- Tasks ---
        tasks = [
            Task(title="Draft wireframes",          description="Prepare 3 homepage layout options", status="todo",        priority="high",   project_id=projects[0].id, created_by=users[0].id, due_date=datetime.datetime.now() + datetime.timedelta(days=7)),
            Task(title="Write copy for About page", description="500 words, friendly tone",          status="in_progress", priority="medium", project_id=projects[0].id, created_by=users[0].id, due_date=datetime.datetime.now() + datetime.timedelta(days=5)),
            Task(title="Implement tracking events", description="Capture button clicks",             status="in_progress", priority="medium", project_id=projects[1].id, created_by=users[1].id, due_date=datetime.datetime.now() + datetime.timedelta(days=14)),
            Task(title="Fix login crash on iOS",    description="Crash on login with special chars", status="todo",        priority="high",   project_id=projects[2].id, created_by=users[0].id, due_date=datetime.datetime.now() + datetime.timedelta(days=2)),
        ]
        for t in tasks:
            session.add(t)
        session.flush()

        # --- Assignments ---
        assignments = [
            Assignment(task_id=tasks[0].id, user_id=users[1].id),
            Assignment(task_id=tasks[0].id, user_id=users[2].id),
            Assignment(task_id=tasks[2].id, user_id=users[3].id),
            Assignment(task_id=tasks[3].id, user_id=users[3].id),
        ]
        for a in assignments:
            session.add(a)
        session.flush()

        # --- Project Members ---
        members = [
            ProjectMember(project_id=projects[0].id, user_id=users[1].id),
            ProjectMember(project_id=projects[0].id, user_id=users[2].id),
            ProjectMember(project_id=projects[1].id, user_id=users[3].id),
        ]
        for m in members:
            session.add(m)
        session.flush()

        # --- Project Notes ---
        project_notes = [
            ProjectNote(content="Kickoff meeting: align on brand colours before wireframes.", project_id=projects[0].id, created_by=users[0].id),
            ProjectNote(content="Client approved the new navigation structure.",               project_id=projects[0].id, created_by=users[1].id),
        ]
        for n in project_notes:
            session.add(n)
        session.flush()

        # --- Task Notes ---
        task_notes = [
            TaskNote(content="Started with mobile layout first — looks cleaner.", task_id=tasks[0].id, created_by=users[1].id),
            TaskNote(content="Copy draft sent to client for review.",              task_id=tasks[1].id, created_by=users[2].id),
        ]
        for n in task_notes:
            session.add(n)

        session.commit()

if __name__ == "__main__":
    from database import db_conn
    db_conn.init()
    seeder = DatabaseSeeder()
    seeder.seed(db_conn.get_session())
    print("Database seeded successfully.")
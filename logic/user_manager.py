# logic/user_manager.py
from pathlib import Path
import sys

import bcrypt

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from database.models import User
from database.connection import DatabaseConnection


class UserManager:

    def __init__(self):
        self.db = DatabaseConnection()
        self.db.init()
        self.session = self.db.get_session()

    def create_user(self, username: str, password: str, is_admin: bool = False) -> User:
        """Creates a new user with a hashed password."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(username=username, password=hashed.decode("utf-8"), is_admin=is_admin)
        self.session.add(user)
        self.session.commit()
        return user

    def delete_user(self, user_id: int) -> bool:
        """Deletes a user by ID. Returns True if successful."""
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def update_user(self, user_id: int, username: str = None, password: str = None) -> User | None:
        """Updates username and/or password for a given user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if username:
            user.username = username
        if password:
            user.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.session.commit()
        return user

    def validate_login(self, username: str, password: str) -> User | None:
        """Returns the User object if credentials are valid, else None."""
        user = self.session.query(User).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None

    def get_user_by_id(self, user_id: int) -> User | None:
        """Fetches a single user by their primary key."""
        return self.session.query(User).filter_by(id=user_id).first()

    def get_all_users(self) -> list[User]:
        """Returns all users (useful for admin views)."""
        return self.session.query(User).all()

    def is_admin(self, user: User) -> bool:
        """Returns True if the user is an admin."""
        return user.is_admin

    def user_exists(self, username: str) -> bool:
        """Checks whether a username is already taken."""
        return self.session.query(User).filter_by(username=username).first() is not None
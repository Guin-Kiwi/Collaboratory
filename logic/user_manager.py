# logic/user_manager.py
from pathlib import Path
import sys

import bcrypt

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from database.models import User
from database import db_conn

class UserManager:
    """Manages user accounts: create, update, delete, and authenticate."""

    def __init__(self, session=None):
        self.session = session or db_conn.get_session()

    def create_user(self, username: str, password: str, name: str, email: str, is_admin: bool = False) -> User:
        """Creates a new user with a hashed password and inserts into the database."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(
            username=username,
            password=hashed.decode("utf-8"),
            name=name,
            email=email,
            is_admin=is_admin
        )
        self.session.add(user)
        self.session.commit()
        return user

    def delete_account(self, user_id: int, password: str) -> bool:
        """Deletes the user's own account after verifying password."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return False
        self.session.delete(user)
        self.session.commit()
        return True

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

    def promote_user_to_admin(self, user_id: int) -> bool:
        """Promotes a user to admin status. Returns True if successful."""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return False

        user.is_admin = True
        self.session.commit()
        return True

    def revoke_admin_status(self, user_id: int) -> bool:
        """Revoke admin status from a user."""
        user = self.get_user_by_id(user_id)

        if not user:
            return False

        user.is_admin = False
        self.session.commit()
        return True
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Resets the user's password to the provided new password.
        
        Args:
            username: The username of the account to reset.
            new_password: The new plain text password to hash and store.
        
        Returns:
            True if the user was found and password updated, False otherwise.
        """
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            return False
        user.password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.session.commit()
        return True
        
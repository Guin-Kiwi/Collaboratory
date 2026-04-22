# logic/user_manager.py

from database.models import User
from database.connection import DatabaseConnection


class UserManager:

    def __init__(self):
        self.db = DatabaseConnection()
        self.db.init()
        self.session = self.db.get_session()

    def validate_login(self, username: str, password: str) -> User | None:
        """Returns the User object if credentials are valid, else None."""
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.password == password:
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
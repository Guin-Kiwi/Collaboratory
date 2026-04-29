"""
Application state manager.

Stores the currently authenticated user during runtime.
Acts as a shared session layer between UI and logic.
"""

from __future__ import annotations

from database.models import User, Assignment


class AppState:
    """Manages the currently logged-in user (application session state)."""

    def __init__(self) -> None:
        self.current_user: User | None = None

    def login(self, user: User) -> None:
        self.current_user = user

    def logout(self) -> None:
        self.current_user = None

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_current_user(self) -> User | None:
        return self.current_user

    def get_current_user_id(self) -> int | None:
        if self.current_user is None:
            return None
        return self.current_user.id

    def get_current_username(self) -> str | None:
        if self.current_user is None:
            return None
        return self.current_user.username

# --- commented out, permissions_manager.py will deal with this
# kept for explaination, to be removed on merge.

    # def get_current_role(self, role: Assignment) -> str | None:
    #     if self.current_user is None:
    #        return None       
    #     return self.current_user.role

    def is_admin(self) -> bool:
        if self.current_user is None:
            return False
        return self.current_user.is_admin
    
    def get_name(self) -> str | None:
        if self.current_user is None:
            return None
        return self.current_user.name


# shared global instance
app_state = AppState()

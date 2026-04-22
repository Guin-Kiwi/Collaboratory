"""Generic base service providing CRUD operations for any ORM model."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from database.models import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseService(Generic[ModelT]):
    """Server-side business-logic layer for a single ORM model type.

    Subclass this for each domain entity and add domain-specific methods::

        class ItemService(BaseService[Item]):
            def find_by_name(self, name: str) -> list[Item]:
                return (
                    self._session.query(self._model_class)
                    .filter(Item.name == name)
                    .all()
                )

    Args:
        model_class: The SQLAlchemy ORM class this service manages.
        session: An active :class:`~sqlalchemy.orm.Session`.
    """

    def __init__(self, model_class: type[ModelT], session: Session) -> None:
        self._model_class = model_class
        self._session = session

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def get_all(self) -> list[ModelT]:
        """Return every row for the managed model."""
        return self._session.query(self._model_class).all()

    def get_by_id(self, record_id: int) -> ModelT | None:
        """Return a single record by primary key, or *None* if not found."""
        return self._session.get(self._model_class, record_id)

    def create(self, **kwargs) -> ModelT:
        """Instantiate, persist, and return a new model record.

        Args:
            **kwargs: Column values passed to the model constructor.

        Returns:
            The newly created and committed model instance.
        """
        instance = self._model_class(**kwargs)
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)
        return instance

    def update(self, record_id: int, **kwargs) -> ModelT | None:
        """Update an existing record's fields and return it.

        Args:
            record_id: Primary-key value of the record to update.
            **kwargs: Column names and their new values.

        Returns:
            The updated instance, or *None* if no record with that id exists.
        """
        instance = self.get_by_id(record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self._session.commit()
        self._session.refresh(instance)
        return instance

    def delete(self, record_id: int) -> bool:
        #if that was sql, it would be 
        # #stringComm = "DELETE from table self.tablename  WHERE id = record_id". but here, we have to first get the ORM instance, then delete it.
        #sqlite.conn(stringComm).execute (conceptually, not actual code!!!)
        """Delete a record by primary key.

        Args:
            record_id: Primary-key value of the record to delete.

        Returns:
            *True* if the record was found and deleted, *False* otherwise.
        """
        instance = self.get_by_id(record_id)
        if instance is None:
            return False
        self._session.delete(instance)
        self._session.commit()
        return True

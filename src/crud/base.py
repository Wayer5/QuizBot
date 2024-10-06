from typing import Optional

from flask_sqlalchemy import model

from src import db


class CRUDBase:

    """Класс для работы с бд через CRUD."""

    def __init__(self, model: model) -> None:
        """Модель бд."""
        self.model = model

    def get(self, obj_id: int) -> Optional[object]:
        """Получить объект."""
        return self.model.query.get_or_404(obj_id)

    def get_multi(self) -> list[object]:
        """Создать список объектов."""
        return self.model.query.all()

    def create(self, obj_in: dict) -> object:
        """Создать обект."""
        db_obj = self.model(**obj_in)
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def update(self, db_obj: object, obj_in: dict) -> object:
        """Обновить объект."""
        obj_data = db_obj.__dict__

        for field in obj_data:
            if field in obj_in:
                setattr(db_obj, field, obj_in[field])
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def update_with_obj(self, obj_in: object) -> object:
        """Обновить объект."""
        db.session.commit()
        db.session.refresh(obj_in)
        return obj_in

    def remove(self, db_obj: object) -> object:
        """Удалить обект."""
        db.session.delete(db_obj)
        db.session.commit()
        return db_obj

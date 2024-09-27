from src import db


class CRUDBase:
    def __init__(self, model):
        self.model = model

    def get(self, obj_id):
        return self.model.query.get(obj_id)

    def get_multi(self):
        return self.model.query.all()

    def create(self, obj_in):
        db_obj = self.model(**obj_in)
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def update(self, db_obj, obj_in):
        obj_data = db_obj.__dict__

        for field in obj_data:
            if field in obj_in:
                setattr(db_obj, field, obj_in[field])
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def remove(self, db_obj):
        db.session.delete(db_obj)
        db.session.commit()
        return db_obj

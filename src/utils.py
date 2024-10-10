from sqlalchemy.inspection import inspect


class Dotdict(dict):

    """Доступ через точку."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def obj_to_dict(obj: object, seen: dict | None = None) -> Dotdict:
    """Создаем словарь из модели (гиперсложный код)."""
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return None
    seen.add(id(obj))

    if isinstance(obj, list):
        return [obj_to_dict(item, seen) for item in obj]
    if isinstance(obj, dict):
        data = Dotdict(obj)
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = obj_to_dict(value, seen)
            elif isinstance(value, list):
                data[key] = [obj_to_dict(item, seen) for item in value]
        return data
    if hasattr(obj, '__dict__'):
        data = Dotdict(
            {
                c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs
            },
        )
        inspect_manager = inspect(obj.__class__)
        relationships = inspect_manager.relationships
        for rel in relationships:
            value = getattr(obj, rel.key)
            data[rel.key] = obj_to_dict(value, seen) if value else None
        return data
    return obj

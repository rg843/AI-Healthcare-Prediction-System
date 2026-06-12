from fastapi import HTTPException
from .db import SessionLocal


def get_or_404(model, id_):
    db = SessionLocal()
    try:
        obj = db.query(model).get(id_)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj
    finally:
        db.close()

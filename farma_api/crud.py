from sqlalchemy.orm import Session

from . import models, schemas


def get_medicament(db: Session, medicament_id: int):
    return db.query(models.Medicament).filter(
        models.Medicament.id == medicament_id
    ).first()

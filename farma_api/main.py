from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return "ok"


@app.get("/users/{user_id}", response_model=schemas.Medicament)
def read_user(medicament_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_medicament(db, medicament_id=medicament_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Medicament not found")
    return db_user

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix='/api/geo', tags=['Géolocalisation'])

@router.get('/communes', response_model=List[schemas.Commune])
def get_communes(db: Session = Depends(get_db)):
    return db.query(models.Commune).all()

@router.get('/communes/{commune_id}/quartiers', response_model=List[schemas.Quartier])
def get_quartiers(commune_id: int, db: Session = Depends(get_db)):
    return db.query(models.Quartier).filter(models.Quartier.commune_id == commune_id).all()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/ecoles', tags=['Écoles'])

@router.post('/', response_model=schemas.Ecole)
def create_ecole(
    ecole: schemas.EcoleCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    db_ecole = models.Ecole(**ecole.dict())
    db.add(db_ecole)
    db.commit()
    db.refresh(db_ecole)
    return db_ecole

@router.get('/', response_model=List[schemas.Ecole])
def get_ecoles(
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    return db.query(models.Ecole).all()

@router.get('/mon-ecole', response_model=schemas.Ecole)
def get_mon_ecole(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    ecole = db.query(models.Ecole).filter(models.Ecole.id == current_user.ecole_id).first()
    if not ecole:
        raise HTTPException(404, 'École introuvable')
    return ecole

@router.put('/mon-ecole', response_model=schemas.Ecole)
def update_mon_ecole(
    ecole_update: schemas.EcoleCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    ecole = db.query(models.Ecole).filter(models.Ecole.id == current_user.ecole_id).first()
    if not ecole:
        raise HTTPException(404, 'École introuvable')
    
    for key, value in ecole_update.dict(exclude_unset=True).items():
        setattr(ecole, key, value)
    
    db.commit()
    db.refresh(ecole)
    return ecole

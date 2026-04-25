from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/echeanciers', tags=['Échéanciers'])

@router.post('/', response_model=schemas.EcheancierOut)
def create_echeancier(
    echeancier: schemas.EcheancierCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    db_echeancier = models.Echeancier(**echeancier.dict(), ecole_id=current_user.ecole_id)
    db.add(db_echeancier)
    db.commit()
    db.refresh(db_echeancier)
    return db_echeancier

@router.get('/', response_model=List[schemas.EcheancierOut])
def get_echeanciers(
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Echeancier).filter(models.Echeancier.ecole_id == current_user.ecole_id)
    if classe_id:
        query = query.filter(models.Echeancier.classe_id == classe_id)
    return query.all()

@router.post('/{echeancier_id}/tranches', response_model=schemas.TrancheOut)
def create_tranche(
    echeancier_id: int,
    tranche: schemas.TrancheCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    echeancier = db.query(models.Echeancier).filter(
        models.Echeancier.id == echeancier_id,
        models.Echeancier.ecole_id == current_user.ecole_id
    ).first()
    if not echeancier:
        raise HTTPException(404, 'Échéancier introuvable')
    
    db_tranche = models.Tranche(**tranche.dict(), echeancier_id=echeancier_id)
    db.add(db_tranche)
    db.commit()
    db.refresh(db_tranche)
    return db_tranche

@router.get('/{echeancier_id}/tranches', response_model=List[schemas.TrancheOut])
def get_tranches(
    echeancier_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    echeancier = db.query(models.Echeancier).filter(
        models.Echeancier.id == echeancier_id,
        models.Echeancier.ecole_id == current_user.ecole_id
    ).first()
    if not echeancier:
        raise HTTPException(404, 'Échéancier introuvable')
    
    return db.query(models.Tranche).filter(
        models.Tranche.echeancier_id == echeancier_id
    ).order_by(models.Tranche.date_echeance).all()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/frais', tags=['Frais Scolaires'])

@router.post('/', response_model=schemas.FraisScolaire)
def create_frais(
    frais: schemas.FraisScolaireCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    db_frais = models.FraisScolaire(**frais.dict(), ecole_id=current_user.ecole_id)
    db.add(db_frais)
    db.commit()
    db.refresh(db_frais)
    return db_frais

@router.get('/', response_model=List[schemas.FraisScolaire])
def get_frais(
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.FraisScolaire).filter(models.FraisScolaire.ecole_id == current_user.ecole_id)
    if classe_id:
        query = query.filter(models.FraisScolaire.classe_id == classe_id)
    return query.all()

@router.put('/{frais_id}', response_model=schemas.FraisScolaire)
def update_frais(
    frais_id: int,
    frais_update: schemas.FraisScolaireCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    frais = db.query(models.FraisScolaire).filter(
        models.FraisScolaire.id == frais_id,
        models.FraisScolaire.ecole_id == current_user.ecole_id
    ).first()
    if not frais:
        raise HTTPException(404, 'Frais introuvable')
    
    for key, value in frais_update.dict(exclude_unset=True).items():
        setattr(frais, key, value)
    
    db.commit()
    db.refresh(frais)
    return frais

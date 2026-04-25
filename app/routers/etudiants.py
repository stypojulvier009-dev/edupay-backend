from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/etudiants', tags=['Étudiants'])

@router.post('/', response_model=schemas.Etudiant)
def create_etudiant(
    etudiant: schemas.EtudiantCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    db_etudiant = models.Etudiant(**etudiant.dict(), ecole_id=current_user.ecole_id)
    db.add(db_etudiant)
    db.commit()
    db.refresh(db_etudiant)
    return db_etudiant

@router.get('/', response_model=List[schemas.Etudiant])
def get_etudiants(
    classe_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Etudiant).filter(models.Etudiant.ecole_id == current_user.ecole_id)
    if classe_id:
        query = query.filter(models.Etudiant.classe_id == classe_id)
    return query.offset(skip).limit(limit).all()

@router.get('/{etudiant_id}', response_model=schemas.Etudiant)
def get_etudiant(
    etudiant_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    etudiant = db.query(models.Etudiant).filter(
        models.Etudiant.id == etudiant_id,
        models.Etudiant.ecole_id == current_user.ecole_id
    ).first()
    if not etudiant:
        raise HTTPException(404, 'Étudiant introuvable')
    return etudiant

@router.put('/{etudiant_id}', response_model=schemas.Etudiant)
def update_etudiant(
    etudiant_id: int,
    etudiant_update: schemas.EtudiantCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    etudiant = db.query(models.Etudiant).filter(
        models.Etudiant.id == etudiant_id,
        models.Etudiant.ecole_id == current_user.ecole_id
    ).first()
    if not etudiant:
        raise HTTPException(404, 'Étudiant introuvable')
    
    for key, value in etudiant_update.dict(exclude_unset=True).items():
        setattr(etudiant, key, value)
    
    db.commit()
    db.refresh(etudiant)
    return etudiant

@router.delete('/{etudiant_id}')
def delete_etudiant(
    etudiant_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    etudiant = db.query(models.Etudiant).filter(
        models.Etudiant.id == etudiant_id,
        models.Etudiant.ecole_id == current_user.ecole_id
    ).first()
    if not etudiant:
        raise HTTPException(404, 'Étudiant introuvable')
    
    db.delete(etudiant)
    db.commit()
    return {'message': 'Étudiant supprimé'}

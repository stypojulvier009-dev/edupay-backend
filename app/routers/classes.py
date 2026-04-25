from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/classes', tags=['Classes'])

@router.post('/', response_model=schemas.Classe)
def create_classe(
    classe: schemas.ClasseCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    db_classe = models.Classe(**classe.dict(), ecole_id=current_user.ecole_id)
    db.add(db_classe)
    db.commit()
    db.refresh(db_classe)
    return db_classe

@router.get('/', response_model=List[schemas.Classe])
def get_classes(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Classe).filter(models.Classe.ecole_id == current_user.ecole_id).all()

@router.get('/{classe_id}', response_model=schemas.Classe)
def get_classe(
    classe_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    classe = db.query(models.Classe).filter(
        models.Classe.id == classe_id,
        models.Classe.ecole_id == current_user.ecole_id
    ).first()
    if not classe:
        raise HTTPException(404, 'Classe introuvable')
    return classe

@router.put('/{classe_id}', response_model=schemas.Classe)
def update_classe(
    classe_id: int,
    classe_update: schemas.ClasseCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    classe = db.query(models.Classe).filter(
        models.Classe.id == classe_id,
        models.Classe.ecole_id == current_user.ecole_id
    ).first()
    if not classe:
        raise HTTPException(404, 'Classe introuvable')
    
    for key, value in classe_update.dict(exclude_unset=True).items():
        setattr(classe, key, value)
    
    db.commit()
    db.refresh(classe)
    return classe

@router.delete('/{classe_id}')
def delete_classe(
    classe_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    classe = db.query(models.Classe).filter(
        models.Classe.id == classe_id,
        models.Classe.ecole_id == current_user.ecole_id
    ).first()
    if not classe:
        raise HTTPException(404, 'Classe introuvable')
    
    db.delete(classe)
    db.commit()
    return {'message': 'Classe supprimée'}

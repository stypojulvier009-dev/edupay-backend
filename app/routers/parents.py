from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/parents', tags=['Parents'])

@router.post('/', response_model=schemas.ParentOut)
def create_parent(
    parent: schemas.ParentCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    db_parent = models.Parent(**parent.dict(), ecole_id=current_user.ecole_id)
    db.add(db_parent)
    db.commit()
    db.refresh(db_parent)
    return db_parent

@router.get('/', response_model=List[schemas.ParentOut])
def get_parents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Parent).filter(
        models.Parent.ecole_id == current_user.ecole_id
    ).offset(skip).limit(limit).all()

@router.get('/{parent_id}', response_model=schemas.ParentOut)
def get_parent(
    parent_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    parent = db.query(models.Parent).filter(
        models.Parent.id == parent_id,
        models.Parent.ecole_id == current_user.ecole_id
    ).first()
    if not parent:
        raise HTTPException(404, 'Parent introuvable')
    return parent

@router.put('/{parent_id}', response_model=schemas.ParentOut)
def update_parent(
    parent_id: int,
    parent_update: schemas.ParentCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    parent = db.query(models.Parent).filter(
        models.Parent.id == parent_id,
        models.Parent.ecole_id == current_user.ecole_id
    ).first()
    if not parent:
        raise HTTPException(404, 'Parent introuvable')
    
    for key, value in parent_update.dict(exclude_unset=True).items():
        setattr(parent, key, value)
    
    db.commit()
    db.refresh(parent)
    return parent

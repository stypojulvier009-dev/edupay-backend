# -*- coding: utf-8 -*-
import os

# Router pour Parents
router_parents = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/parents', tags=['Parents'])

@router.post('/', response_model=schemas.Parent)
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

@router.get('/', response_model=List[schemas.Parent])
def get_parents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Parent).filter(
        models.Parent.ecole_id == current_user.ecole_id
    ).offset(skip).limit(limit).all()

@router.get('/{parent_id}', response_model=schemas.Parent)
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

@router.put('/{parent_id}', response_model=schemas.Parent)
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
'''

# Router pour Étudiants
router_etudiants = '''from fastapi import APIRouter, Depends, HTTPException
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
'''

# Router pour Frais Scolaires
router_frais = '''from fastapi import APIRouter, Depends, HTTPException
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
'''

with open(r'E:\mon app\edupay\backend\app\routers\parents.py', 'w', encoding='utf-8') as f:
    f.write(router_parents)

with open(r'E:\mon app\edupay\backend\app\routers\etudiants.py', 'w', encoding='utf-8') as f:
    f.write(router_etudiants)

with open(r'E:\mon app\edupay\backend\app\routers\frais.py', 'w', encoding='utf-8') as f:
    f.write(router_frais)

print('OK - Routers parents, etudiants, frais crees!')

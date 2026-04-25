# -*- coding: utf-8 -*-
import os

# Router pour Paiements
router_paiements = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/paiements', tags=['Paiements'])

@router.post('/', response_model=schemas.Paiement)
def create_paiement(
    paiement: schemas.PaiementCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable', 'caissier']:
        raise HTTPException(403, 'Permission refusée')
    
    db_paiement = models.Paiement(
        **paiement.dict(),
        ecole_id=current_user.ecole_id,
        utilisateur_id=current_user.id
    )
    db.add(db_paiement)
    db.commit()
    db.refresh(db_paiement)
    
    # Créer notification
    notification = models.Notification(
        ecole_id=current_user.ecole_id,
        utilisateur_id=db_paiement.etudiant.parent_id,
        type='paiement',
        titre='Paiement reçu',
        message=f'Paiement de {paiement.montant} {paiement.devise} reçu pour {db_paiement.etudiant.nom}',
        canal='sms'
    )
    db.add(notification)
    db.commit()
    
    return db_paiement

@router.get('/', response_model=List[schemas.Paiement])
def get_paiements(
    etudiant_id: int = None,
    date_debut: str = None,
    date_fin: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Paiement).filter(models.Paiement.ecole_id == current_user.ecole_id)
    
    if etudiant_id:
        query = query.filter(models.Paiement.etudiant_id == etudiant_id)
    if date_debut:
        query = query.filter(models.Paiement.date_paiement >= date_debut)
    if date_fin:
        query = query.filter(models.Paiement.date_paiement <= date_fin)
    
    return query.order_by(models.Paiement.date_paiement.desc()).offset(skip).limit(limit).all()

@router.get('/{paiement_id}', response_model=schemas.Paiement)
def get_paiement(
    paiement_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    paiement = db.query(models.Paiement).filter(
        models.Paiement.id == paiement_id,
        models.Paiement.ecole_id == current_user.ecole_id
    ).first()
    if not paiement:
        raise HTTPException(404, 'Paiement introuvable')
    return paiement

@router.get('/stats/dashboard')
def get_stats_paiements(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    
    total = db.query(func.sum(models.Paiement.montant)).filter(
        models.Paiement.ecole_id == current_user.ecole_id
    ).scalar() or 0
    
    aujourd_hui = db.query(func.sum(models.Paiement.montant)).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        func.date(models.Paiement.date_paiement) == datetime.now().date()
    ).scalar() or 0
    
    return {
        'total': float(total),
        'aujourd_hui': float(aujourd_hui),
        'nombre_paiements': db.query(models.Paiement).filter(
            models.Paiement.ecole_id == current_user.ecole_id
        ).count()
    }
'''

# Router pour Échéanciers
router_echeanciers = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/echeanciers', tags=['Échéanciers'])

@router.post('/', response_model=schemas.Echeancier)
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

@router.get('/', response_model=List[schemas.Echeancier])
def get_echeanciers(
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Echeancier).filter(models.Echeancier.ecole_id == current_user.ecole_id)
    if classe_id:
        query = query.filter(models.Echeancier.classe_id == classe_id)
    return query.all()

@router.post('/{echeancier_id}/tranches', response_model=schemas.Tranche)
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

@router.get('/{echeancier_id}/tranches', response_model=List[schemas.Tranche])
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
'''

with open(r'E:\mon app\edupay\backend\app\routers\paiements.py', 'w', encoding='utf-8') as f:
    f.write(router_paiements)

with open(r'E:\mon app\edupay\backend\app\routers\echeanciers.py', 'w', encoding='utf-8') as f:
    f.write(router_echeanciers)

print('OK - Routers paiements et echeanciers crees!')

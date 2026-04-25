# -*- coding: utf-8 -*-
import os

# Router pour Notifications
router_notifications = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/notifications', tags=['Notifications'])

@router.post('/', response_model=schemas.Notification)
def create_notification(
    notification: schemas.NotificationCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    db_notification = models.Notification(**notification.dict(), ecole_id=current_user.ecole_id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get('/', response_model=List[schemas.Notification])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Notification).filter(
        models.Notification.utilisateur_id == current_user.id
    ).order_by(models.Notification.date_creation.desc()).offset(skip).limit(limit).all()

@router.put('/{notification_id}/lire')
def marquer_lu(
    notification_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.utilisateur_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(404, 'Notification introuvable')
    
    notification.lu = True
    db.commit()
    return {'message': 'Notification marquée comme lue'}
'''

# Router pour Rapports
router_rapports = '''from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/rapports', tags=['Rapports'])

@router.post('/generer', response_model=schemas.Rapport)
def generer_rapport(
    rapport: schemas.RapportCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    db_rapport = models.Rapport(
        **rapport.dict(),
        ecole_id=current_user.ecole_id,
        genere_par=current_user.id
    )
    db.add(db_rapport)
    db.commit()
    db.refresh(db_rapport)
    return db_rapport

@router.get('/', response_model=List[schemas.Rapport])
def get_rapports(
    skip: int = 0,
    limit: int = 50,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Rapport).filter(
        models.Rapport.ecole_id == current_user.ecole_id
    ).order_by(models.Rapport.date_generation.desc()).offset(skip).limit(limit).all()

@router.get('/stats/financier')
def stats_financier(
    date_debut: str,
    date_fin: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    
    paiements = db.query(
        func.sum(models.Paiement.montant).label('total'),
        func.count(models.Paiement.id).label('nombre'),
        models.Paiement.mode_paiement
    ).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        models.Paiement.date_paiement >= date_debut,
        models.Paiement.date_paiement <= date_fin
    ).group_by(models.Paiement.mode_paiement).all()
    
    return {
        'periode': {'debut': date_debut, 'fin': date_fin},
        'paiements': [
            {
                'mode': p.mode_paiement,
                'total': float(p.total or 0),
                'nombre': p.nombre
            } for p in paiements
        ]
    }

@router.get('/stats/etudiants')
def stats_etudiants(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    
    par_classe = db.query(
        models.Classe.nom,
        func.count(models.Etudiant.id).label('nombre')
    ).join(models.Etudiant).filter(
        models.Classe.ecole_id == current_user.ecole_id
    ).group_by(models.Classe.nom).all()
    
    return {
        'total': db.query(models.Etudiant).filter(
            models.Etudiant.ecole_id == current_user.ecole_id
        ).count(),
        'par_classe': [{'classe': c.nom, 'nombre': c.nombre} for c in par_classe]
    }
'''

# Router pour Audit Logs
router_audit = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth
from .database import get_db

router = APIRouter(prefix='/api/audit', tags=['Audit'])

@router.post('/', response_model=schemas.AuditLog)
def create_audit_log(
    log: schemas.AuditLogCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_log = models.AuditLog(
        **log.dict(),
        ecole_id=current_user.ecole_id,
        utilisateur_id=current_user.id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get('/', response_model=List[schemas.AuditLog])
def get_audit_logs(
    action: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    query = db.query(models.AuditLog).filter(models.AuditLog.ecole_id == current_user.ecole_id)
    
    if action:
        query = query.filter(models.AuditLog.action == action)
    
    return query.order_by(models.AuditLog.date_action.desc()).offset(skip).limit(limit).all()
'''

with open(r'E:\mon app\edupay\backend\app\routers\notifications.py', 'w', encoding='utf-8') as f:
    f.write(router_notifications)

with open(r'E:\mon app\edupay\backend\app\routers\rapports.py', 'w', encoding='utf-8') as f:
    f.write(router_rapports)

with open(r'E:\mon app\edupay\backend\app\routers\audit.py', 'w', encoding='utf-8') as f:
    f.write(router_audit)

print('OK - Routers notifications, rapports, audit crees!')

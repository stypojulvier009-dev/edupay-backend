from fastapi import APIRouter, Depends, HTTPException
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

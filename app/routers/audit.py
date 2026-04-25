from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/audit', tags=['Audit'])

@router.post('/', response_model=schemas.UtilisateurOut)
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

@router.get('/', response_model=List[schemas.UtilisateurOut])
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

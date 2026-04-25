from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/abonnements', tags=['Abonnements'])

@router.get('/', response_model=List[schemas.Abonnement])
def get_abonnements(db: Session = Depends(get_db)):
    return db.query(models.Abonnement).filter(models.Abonnement.actif == True).all()

@router.post('/souscrire', response_model=schemas.Souscription)
def souscrire(
    souscription: schemas.SouscriptionCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ['super_admin', 'admin_ecole']:
        raise HTTPException(403, 'Permission refusée')
    
    abonnement = db.query(models.Abonnement).filter(models.Abonnement.id == souscription.abonnement_id).first()
    if not abonnement:
        raise HTTPException(404, 'Abonnement introuvable')
    
    db_souscription = models.Souscription(**souscription.dict(), ecole_id=current_user.ecole_id)
    db.add(db_souscription)
    db.commit()
    db.refresh(db_souscription)
    return db_souscription

@router.get('/ma-souscription', response_model=schemas.Souscription)
def get_ma_souscription(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    souscription = db.query(models.Souscription).filter(
        models.Souscription.ecole_id == current_user.ecole_id,
        models.Souscription.actif == True
    ).first()
    if not souscription:
        raise HTTPException(404, 'Aucune souscription active')
    return souscription

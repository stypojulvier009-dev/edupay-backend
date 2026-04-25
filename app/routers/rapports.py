from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/rapports', tags=['Rapports'])

@router.post('/generer', response_model=schemas.RapportFinancier)
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

@router.get('/', response_model=List[schemas.RapportFinancier])
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

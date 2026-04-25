from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/presences', tags=['Présences'])

# ══════════════════════════════════════════════════════════════
# ENREGISTREMENT DES PRESENCES
# ══════════════════════════════════════════════════════════════

@router.post('/enregistrer')
def enregistrer_presence(
    etudiant_id: int,
    classe_id: int,
    date: str,
    present: bool = True,
    retard: bool = False,
    justifie: bool = False,
    motif_absence: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Enregistrer la présence d'un étudiant"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'enseignant']:
        raise HTTPException(403, 'Permission refusée')
    
    # Vérifier si déjà enregistré
    existing = db.query(models.Presence).filter(
        models.Presence.etudiant_id == etudiant_id,
        models.Presence.date == date
    ).first()
    
    if existing:
        existing.present = present
        existing.retard = retard
        existing.justifie = justifie
        existing.motif_absence = motif_absence
    else:
        presence = models.Presence(
            etudiant_id=etudiant_id,
            classe_id=classe_id,
            date=date,
            present=present,
            retard=retard,
            justifie=justifie,
            motif_absence=motif_absence,
            enregistre_par=current_user.id
        )
        db.add(presence)
    
    db.commit()
    return {'success': True, 'message': 'Présence enregistrée'}

@router.post('/enregistrer-classe')
def enregistrer_presences_classe(
    classe_id: int,
    date: str,
    presences: List[dict],  # [{etudiant_id, present, retard}]
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Enregistrer les présences de toute une classe"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'enseignant']:
        raise HTTPException(403, 'Permission refusée')
    
    for p in presences:
        existing = db.query(models.Presence).filter(
            models.Presence.etudiant_id == p['etudiant_id'],
            models.Presence.date == date
        ).first()
        
        if existing:
            existing.present = p.get('present', True)
            existing.retard = p.get('retard', False)
        else:
            presence = models.Presence(
                etudiant_id=p['etudiant_id'],
                classe_id=classe_id,
                date=date,
                present=p.get('present', True),
                retard=p.get('retard', False),
                enregistre_par=current_user.id
            )
            db.add(presence)
    
    db.commit()
    return {'success': True, 'message': f'{len(presences)} présences enregistrées'}

# ══════════════════════════════════════════════════════════════
# CONSULTATION DES PRESENCES
# ══════════════════════════════════════════════════════════════

@router.get('/classe/{classe_id}')
def get_presences_classe(
    classe_id: int,
    date: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des présences d'une classe pour une date"""
    presences = db.query(models.Presence).filter(
        models.Presence.classe_id == classe_id,
        models.Presence.date == date
    ).all()
    
    return presences

@router.get('/etudiant/{etudiant_id}')
def get_presences_etudiant(
    etudiant_id: int,
    date_debut: str = None,
    date_fin: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Historique des présences d'un étudiant"""
    query = db.query(models.Presence).filter(
        models.Presence.etudiant_id == etudiant_id
    )
    
    if date_debut:
        query = query.filter(models.Presence.date >= date_debut)
    if date_fin:
        query = query.filter(models.Presence.date <= date_fin)
    
    return query.order_by(models.Presence.date.desc()).all()

# ══════════════════════════════════════════════════════════════
# ABSENTS DU JOUR
# ══════════════════════════════════════════════════════════════

@router.get('/absents')
def get_absents_du_jour(
    date: str = None,
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des absents du jour"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    query = db.query(models.Presence).filter(
        models.Presence.date == date,
        models.Presence.present == False
    )
    
    if classe_id:
        query = query.filter(models.Presence.classe_id == classe_id)
    
    absents = query.all()
    
    return {
        'date': date,
        'total_absents': len(absents),
        'absents': [
            {
                'etudiant': {
                    'id': a.etudiant.id,
                    'nom': a.etudiant.nom,
                    'prenom': a.etudiant.prenom,
                    'matricule': a.etudiant.matricule,
                    'classe': a.classe.nom if a.classe else None
                },
                'justifie': a.justifie,
                'motif': a.motif_absence
            }
            for a in absents
        ]
    }

# ══════════════════════════════════════════════════════════════
# RAPPORTS D'ABSENCES
# ══════════════════════════════════════════════════════════════

@router.get('/rapport/{etudiant_id}')
def get_rapport_absences(
    etudiant_id: int,
    periode_debut: str,
    periode_fin: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Générer un rapport d'absences pour un étudiant"""
    from sqlalchemy import func
    
    presences = db.query(models.Presence).filter(
        models.Presence.etudiant_id == etudiant_id,
        models.Presence.date >= periode_debut,
        models.Presence.date <= periode_fin
    ).all()
    
    total_jours = len(presences)
    jours_presents = sum(1 for p in presences if p.present)
    jours_absents = sum(1 for p in presences if not p.present)
    jours_retard = sum(1 for p in presences if p.retard)
    taux_presence = (jours_presents / total_jours * 100) if total_jours > 0 else 0
    
    # Créer le rapport
    rapport = models.RapportAbsence(
        etudiant_id=etudiant_id,
        periode_debut=periode_debut,
        periode_fin=periode_fin,
        total_jours=total_jours,
        jours_presents=jours_presents,
        jours_absents=jours_absents,
        jours_retard=jours_retard,
        taux_presence=taux_presence
    )
    db.add(rapport)
    db.commit()
    
    return {
        'etudiant_id': etudiant_id,
        'periode': {'debut': periode_debut, 'fin': periode_fin},
        'total_jours': total_jours,
        'jours_presents': jours_presents,
        'jours_absents': jours_absents,
        'jours_retard': jours_retard,
        'taux_presence': round(taux_presence, 2)
    }

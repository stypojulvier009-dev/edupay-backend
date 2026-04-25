from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/examens', tags=['Examens'])

# ══════════════════════════════════════════════════════════════
# GESTION DES EXAMENS
# ══════════════════════════════════════════════════════════════

@router.post('/')
def create_examen(
    classe_id: int,
    matiere_id: int,
    professeur_id: int,
    titre: str,
    type: str,
    date_examen: str,
    duree_minutes: int,
    note_max: float = 20.0,
    coefficient: float = 1.0,
    salle: str = None,
    description: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un examen"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    examen = models.Examen(
        classe_id=classe_id,
        matiere_id=matiere_id,
        professeur_id=professeur_id,
        titre=titre,
        type=type,
        date_examen=date_examen,
        duree_minutes=duree_minutes,
        note_max=note_max,
        coefficient=coefficient,
        salle=salle,
        description=description
    )
    db.add(examen)
    db.commit()
    db.refresh(examen)
    return examen

@router.get('/classe/{classe_id}')
def get_examens_classe(
    classe_id: int,
    type: str = None,
    date_debut: str = None,
    date_fin: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des examens d'une classe"""
    query = db.query(models.Examen).filter(
        models.Examen.classe_id == classe_id
    )
    
    if type:
        query = query.filter(models.Examen.type == type)
    if date_debut:
        query = query.filter(models.Examen.date_examen >= date_debut)
    if date_fin:
        query = query.filter(models.Examen.date_examen <= date_fin)
    
    return query.order_by(models.Examen.date_examen).all()

@router.get('/du-jour')
def get_examens_du_jour(
    date: str,
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Examens du jour"""
    query = db.query(models.Examen).filter(
        models.Examen.date_examen == date
    )
    
    if classe_id:
        query = query.filter(models.Examen.classe_id == classe_id)
    
    examens = query.all()
    
    return {
        'date': date,
        'total_examens': len(examens),
        'examens': [
            {
                'id': e.id,
                'titre': e.titre,
                'type': e.type,
                'classe': e.classe.nom,
                'matiere': e.matiere.nom,
                'professeur': f"{e.professeur.utilisateur.prenom} {e.professeur.utilisateur.nom}",
                'heure': e.date_examen,
                'duree': e.duree_minutes,
                'salle': e.salle
            }
            for e in examens
        ]
    }

@router.put('/{examen_id}')
def update_examen(
    examen_id: int,
    titre: str = None,
    date_examen: str = None,
    salle: str = None,
    publie: bool = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier un examen"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    examen = db.query(models.Examen).filter(
        models.Examen.id == examen_id
    ).first()
    if not examen:
        raise HTTPException(404, 'Examen introuvable')
    
    if titre:
        examen.titre = titre
    if date_examen:
        examen.date_examen = date_examen
    if salle:
        examen.salle = salle
    if publie is not None:
        examen.publie = publie
    
    db.commit()
    db.refresh(examen)
    return examen

@router.delete('/{examen_id}')
def delete_examen(
    examen_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Supprimer un examen"""
    examen = db.query(models.Examen).filter(
        models.Examen.id == examen_id
    ).first()
    if not examen:
        raise HTTPException(404, 'Examen introuvable')
    
    db.delete(examen)
    db.commit()
    return {'success': True, 'message': 'Examen supprimé'}

# ══════════════════════════════════════════════════════════════
# GESTION DES NOTES
# ══════════════════════════════════════════════════════════════

@router.post('/{examen_id}/notes')
def enregistrer_note(
    examen_id: int,
    etudiant_id: int,
    note: float,
    absent: bool = False,
    appreciation: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Enregistrer une note"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'enseignant']:
        raise HTTPException(403, 'Permission refusée')
    
    # Vérifier si la note existe déjà
    existing = db.query(models.Note).filter(
        models.Note.examen_id == examen_id,
        models.Note.etudiant_id == etudiant_id
    ).first()
    
    if existing:
        existing.note = note
        existing.absent = absent
        existing.appreciation = appreciation
        db_note = existing
    else:
        db_note = models.Note(
            examen_id=examen_id,
            etudiant_id=etudiant_id,
            note=note,
            absent=absent,
            appreciation=appreciation,
            enregistre_par=current_user.id
        )
        db.add(db_note)
    
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get('/{examen_id}/notes')
def get_notes_examen(
    examen_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des notes d'un examen"""
    notes = db.query(models.Note).filter(
        models.Note.examen_id == examen_id
    ).all()
    
    return [
        {
            'etudiant': {
                'id': n.etudiant.id,
                'nom': n.etudiant.nom,
                'prenom': n.etudiant.prenom,
                'matricule': n.etudiant.matricule
            },
            'note': n.note,
            'note_max': n.note_max,
            'absent': n.absent,
            'appreciation': n.appreciation
        }
        for n in notes
    ]

@router.get('/etudiant/{etudiant_id}')
def get_notes_etudiant(
    etudiant_id: int,
    trimestre: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Notes d'un étudiant"""
    query = db.query(models.Note).filter(
        models.Note.etudiant_id == etudiant_id
    )
    
    notes = query.all()
    
    return [
        {
            'examen': {
                'id': n.examen.id,
                'titre': n.examen.titre,
                'type': n.examen.type,
                'matiere': n.examen.matiere.nom,
                'date': n.examen.date_examen,
                'coefficient': n.examen.coefficient
            },
            'note': n.note,
            'note_max': n.note_max,
            'absent': n.absent,
            'appreciation': n.appreciation
        }
        for n in notes
    ]

# ══════════════════════════════════════════════════════════════
# ELIGIBILITE AUX EXAMENS
# ══════════════════════════════════════════════════════════════

@router.get('/{examen_id}/eligibilite')
def verifier_eligibilite(
    examen_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Vérifier l'éligibilité des étudiants pour un examen"""
    examen = db.query(models.Examen).filter(
        models.Examen.id == examen_id
    ).first()
    if not examen:
        raise HTTPException(404, 'Examen introuvable')
    
    # Récupérer tous les étudiants de la classe
    etudiants = db.query(models.Etudiant).filter(
        models.Etudiant.classe_id == examen.classe_id
    ).all()
    
    eligibilites = []
    for etudiant in etudiants:
        # Vérifier les paiements
        paiements_a_jour = True  # TODO: Vérifier les paiements
        
        # Vérifier les présences
        presences = db.query(models.Presence).filter(
            models.Presence.etudiant_id == etudiant.id,
            models.Presence.present == True
        ).count()
        presence_suffisante = presences >= 10  # Minimum 10 présences
        
        eligible = paiements_a_jour and presence_suffisante
        
        eligibilites.append({
            'etudiant': {
                'id': etudiant.id,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom,
                'matricule': etudiant.matricule
            },
            'eligible': eligible,
            'paiement_a_jour': paiements_a_jour,
            'presence_suffisante': presence_suffisante
        })
    
    return {
        'examen': examen.titre,
        'total_etudiants': len(etudiants),
        'eligibles': sum(1 for e in eligibilites if e['eligible']),
        'non_eligibles': sum(1 for e in eligibilites if not e['eligible']),
        'details': eligibilites
    }

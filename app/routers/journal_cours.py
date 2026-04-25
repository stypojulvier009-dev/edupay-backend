from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/journal-classe', tags=['Journal de Classe'])

# ══════════════════════════════════════════════════════════════
# JOURNAL DE CLASSE
# ══════════════════════════════════════════════════════════════

@router.post('/')
def create_journal_entry(
    classe_id: int,
    date: str,
    titre: str,
    contenu: str,
    type: str,
    matiere: str = None,
    visible_parents: bool = True,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Ajouter une entrée au journal de classe"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'enseignant']:
        raise HTTPException(403, 'Permission refusée')
    
    journal = models.JournalClasse(
        classe_id=classe_id,
        date=date,
        titre=titre,
        contenu=contenu,
        type=type,
        matiere=matiere,
        professeur_id=current_user.id if current_user.role == 'enseignant' else None,
        visible_parents=visible_parents
    )
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal

@router.get('/classe/{classe_id}')
def get_journal_classe(
    classe_id: int,
    date_debut: str = None,
    date_fin: str = None,
    type: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Consulter le journal d'une classe"""
    query = db.query(models.JournalClasse).filter(
        models.JournalClasse.classe_id == classe_id
    )
    
    if date_debut:
        query = query.filter(models.JournalClasse.date >= date_debut)
    if date_fin:
        query = query.filter(models.JournalClasse.date <= date_fin)
    if type:
        query = query.filter(models.JournalClasse.type == type)
    
    return query.order_by(models.JournalClasse.date.desc()).all()

@router.put('/{journal_id}')
def update_journal_entry(
    journal_id: int,
    titre: str = None,
    contenu: str = None,
    visible_parents: bool = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier une entrée du journal"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    journal = db.query(models.JournalClasse).filter(
        models.JournalClasse.id == journal_id
    ).first()
    if not journal:
        raise HTTPException(404, 'Entrée introuvable')
    
    if titre:
        journal.titre = titre
    if contenu:
        journal.contenu = contenu
    if visible_parents is not None:
        journal.visible_parents = visible_parents
    
    db.commit()
    db.refresh(journal)
    return journal

@router.delete('/{journal_id}')
def delete_journal_entry(
    journal_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Supprimer une entrée du journal"""
    journal = db.query(models.JournalClasse).filter(
        models.JournalClasse.id == journal_id
    ).first()
    if not journal:
        raise HTTPException(404, 'Entrée introuvable')
    
    db.delete(journal)
    db.commit()
    return {'success': True, 'message': 'Entrée supprimée'}

# ══════════════════════════════════════════════════════════════
# MATIERES
# ══════════════════════════════════════════════════════════════

@router.post('/matieres')
def create_matiere(
    nom: str,
    code: str,
    coefficient: float = 1.0,
    description: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Créer une matière"""
    matiere = models.Matiere(
        nom=nom,
        code=code,
        coefficient=coefficient,
        description=description,
        ecole_id=current_user.ecole_id
    )
    db.add(matiere)
    db.commit()
    db.refresh(matiere)
    return matiere

@router.get('/matieres')
def get_matieres(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des matières"""
    return db.query(models.Matiere).filter(
        models.Matiere.ecole_id == current_user.ecole_id
    ).all()

# ══════════════════════════════════════════════════════════════
# COURS ET EMPLOI DU TEMPS
# ══════════════════════════════════════════════════════════════

@router.post('/cours')
def create_cours(
    classe_id: int,
    matiere_id: int,
    professeur_id: int,
    jour_semaine: str,
    heure_debut: str,
    heure_fin: str,
    salle: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Créer un cours dans l'emploi du temps"""
    cours = models.Cours(
        classe_id=classe_id,
        matiere_id=matiere_id,
        professeur_id=professeur_id,
        jour_semaine=jour_semaine,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        salle=salle
    )
    db.add(cours)
    db.commit()
    db.refresh(cours)
    return cours

@router.get('/cours/classe/{classe_id}')
def get_emploi_du_temps(
    classe_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Emploi du temps d'une classe"""
    cours = db.query(models.Cours).filter(
        models.Cours.classe_id == classe_id,
        models.Cours.actif == True
    ).all()
    
    # Grouper par jour
    emploi = {}
    for c in cours:
        if c.jour_semaine not in emploi:
            emploi[c.jour_semaine] = []
        emploi[c.jour_semaine].append({
            'id': c.id,
            'matiere': c.matiere.nom,
            'professeur': f"{c.professeur.utilisateur.prenom} {c.professeur.utilisateur.nom}",
            'heure_debut': c.heure_debut,
            'heure_fin': c.heure_fin,
            'salle': c.salle
        })
    
    return emploi

@router.get('/cours/du-jour')
def get_cours_du_jour(
    jour_semaine: str,
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Cours du jour"""
    query = db.query(models.Cours).filter(
        models.Cours.jour_semaine == jour_semaine,
        models.Cours.actif == True
    )
    
    if classe_id:
        query = query.filter(models.Cours.classe_id == classe_id)
    
    return query.order_by(models.Cours.heure_debut).all()

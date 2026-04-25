from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/admin/utilisateurs', tags=['Admin - Utilisateurs'])

# ══════════════════════════════════════════════════════════════
# GESTION DES DEMANDES D'INSCRIPTION
# ══════════════════════════════════════════════════════════════

@router.get('/demandes')
def get_demandes_inscription(
    statut: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Liste des demandes d'inscription en attente"""
    query = db.query(models.DemandeInscription)
    if statut:
        query = query.filter(models.DemandeInscription.statut == statut)
    return query.order_by(models.DemandeInscription.date_demande.desc()).all()

@router.post('/demandes/{demande_id}/approuver')
def approuver_demande(
    demande_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Approuver une demande et créer le compte utilisateur"""
    demande = db.query(models.DemandeInscription).filter(
        models.DemandeInscription.id == demande_id
    ).first()
    if not demande:
        raise HTTPException(404, 'Demande introuvable')
    
    # Créer l'utilisateur
    utilisateur = models.Utilisateur(
        nom=demande.nom,
        prenom=demande.prenom,
        email=demande.email,
        telephone=demande.telephone,
        mot_de_passe_hash=demande.mot_de_passe_hash,
        role=demande.role_demande,
        ecole_id=current_user.ecole_id,
        photo_url=demande.photo_url,
        actif=True
    )
    db.add(utilisateur)
    
    # Mettre à jour la demande
    demande.statut = 'approuve'
    demande.date_traitement = datetime.utcnow()
    demande.traite_par = current_user.id
    
    db.commit()
    return {'success': True, 'message': 'Utilisateur créé avec succès'}

@router.post('/demandes/{demande_id}/rejeter')
def rejeter_demande(
    demande_id: int,
    motif: str,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Rejeter une demande d'inscription"""
    demande = db.query(models.DemandeInscription).filter(
        models.DemandeInscription.id == demande_id
    ).first()
    if not demande:
        raise HTTPException(404, 'Demande introuvable')
    
    demande.statut = 'rejete'
    demande.motif_rejet = motif
    demande.date_traitement = datetime.utcnow()
    demande.traite_par = current_user.id
    
    db.commit()
    return {'success': True, 'message': 'Demande rejetée'}

# ══════════════════════════════════════════════════════════════
# GESTION DES UTILISATEURS
# ══════════════════════════════════════════════════════════════

@router.get('/')
def get_utilisateurs(
    role: str = None,
    actif: bool = None,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Liste de tous les utilisateurs"""
    query = db.query(models.Utilisateur).filter(
        models.Utilisateur.ecole_id == current_user.ecole_id
    )
    if role:
        query = query.filter(models.Utilisateur.role == role)
    if actif is not None:
        query = query.filter(models.Utilisateur.actif == actif)
    return query.all()

@router.post('/')
def create_utilisateur(
    utilisateur: schemas.UtilisateurCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Créer un nouvel utilisateur"""
    # Vérifier si l'email existe
    existing = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == utilisateur.email
    ).first()
    if existing:
        raise HTTPException(400, 'Email déjà utilisé')
    
    hashed_password = auth.get_password_hash(utilisateur.mot_de_passe)
    db_user = models.Utilisateur(
        **utilisateur.dict(exclude={'mot_de_passe'}),
        mot_de_passe_hash=hashed_password,
        ecole_id=current_user.ecole_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put('/{utilisateur_id}')
def update_utilisateur(
    utilisateur_id: int,
    utilisateur_update: schemas.UtilisateurCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Modifier un utilisateur"""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id,
        models.Utilisateur.ecole_id == current_user.ecole_id
    ).first()
    if not utilisateur:
        raise HTTPException(404, 'Utilisateur introuvable')
    
    for key, value in utilisateur_update.dict(exclude_unset=True, exclude={'mot_de_passe'}).items():
        setattr(utilisateur, key, value)
    
    if utilisateur_update.mot_de_passe:
        utilisateur.mot_de_passe_hash = auth.get_password_hash(utilisateur_update.mot_de_passe)
    
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

@router.delete('/{utilisateur_id}')
def delete_utilisateur(
    utilisateur_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Supprimer un utilisateur"""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id,
        models.Utilisateur.ecole_id == current_user.ecole_id
    ).first()
    if not utilisateur:
        raise HTTPException(404, 'Utilisateur introuvable')
    
    db.delete(utilisateur)
    db.commit()
    return {'success': True, 'message': 'Utilisateur supprimé'}

@router.put('/{utilisateur_id}/activer')
def activer_utilisateur(
    utilisateur_id: int,
    actif: bool,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Activer/Désactiver un utilisateur"""
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id == utilisateur_id,
        models.Utilisateur.ecole_id == current_user.ecole_id
    ).first()
    if not utilisateur:
        raise HTTPException(404, 'Utilisateur introuvable')
    
    utilisateur.actif = actif
    db.commit()
    return {'success': True, 'message': f'Utilisateur {"activé" if actif else "désactivé"}'}

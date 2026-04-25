from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db
import secrets

router = APIRouter(prefix='/api/paiements', tags=['Paiements'])

# ══════════════════════════════════════════════════════════════
# ENREGISTRER UN PAIEMENT (TOUS MOYENS)
# ══════════════════════════════════════════════════════════════

@router.post('/enregistrer')
def enregistrer_paiement(
    etudiant_id: int,
    montant: float,
    devise: str,
    type_frais: str,
    mode_paiement: str,
    # Details selon le mode
    numero_telephone: Optional[str] = None,
    nom_expediteur: Optional[str] = None,
    code_mtcn: Optional[str] = None,
    agence_nom: Optional[str] = None,
    numero_compte: Optional[str] = None,
    nom_banque: Optional[str] = None,
    numero_cheque: Optional[str] = None,
    numero_bordereau: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enregistre un paiement avec n'importe quel moyen de paiement
    
    Moyens supportes:
    - Mobile Money: mpesa, airtel_money, orange_money, afrimoney
    - Agences: western_union, moneygram, ria, worldremit
    - Banques: rawbank, equity_bank, tmb, sofibanque, ecobank, bgfi
    - Autres: especes, cheque, virement, carte_bancaire
    """
    
    # Verifier l'etudiant
    etudiant = db.query(models.Etudiant).filter(
        models.Etudiant.id == etudiant_id,
        models.Etudiant.ecole_id == current_user.ecole_id
    ).first()
    if not etudiant:
        raise HTTPException(404, 'Etudiant introuvable')
    
    # Verifier que le mode de paiement est actif
    config = db.query(models.ConfigurationPaiement).filter(
        models.ConfigurationPaiement.mode_paiement == mode_paiement,
        models.ConfigurationPaiement.actif == True
    ).first()
    if not config:
        raise HTTPException(400, f'Mode de paiement {mode_paiement} non disponible')
    
    # Verifier les limites
    if montant < config.montant_min:
        raise HTTPException(400, f'Montant minimum: {config.montant_min} {devise}')
    if config.montant_max and montant > config.montant_max:
        raise HTTPException(400, f'Montant maximum: {config.montant_max} {devise}')
    
    # Calculer les frais
    frais = (montant * config.frais_pourcentage / 100) + config.frais_fixe
    montant_net = montant - frais
    
    # Generer reference unique
    reference = f"OASIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
    numero_recu = f"REC-{datetime.now().strftime('%Y%m%d')}-{db.query(models.Paiement).count() + 1:05d}"
    
    # Creer le paiement
    paiement = models.Paiement(
        etudiant_id=etudiant_id,
        ecole_id=current_user.ecole_id,
        montant=montant,
        devise=devise,
        type_frais=type_frais,
        mode_paiement=mode_paiement,
        statut=models.StatutPaiementEnum.VALIDE if mode_paiement == 'especes' else models.StatutPaiementEnum.EN_ATTENTE,
        reference=reference,
        numero_recu=numero_recu,
        numero_telephone=numero_telephone,
        nom_expediteur=nom_expediteur,
        code_mtcn=code_mtcn,
        agence_nom=agence_nom,
        numero_compte=numero_compte,
        nom_banque=nom_banque,
        numero_cheque=numero_cheque,
        numero_bordereau=numero_bordereau,
        frais_transaction=frais,
        montant_net=montant_net,
        notes=notes,
        enregistre_par=current_user.id
    )
    
    db.add(paiement)
    db.commit()
    db.refresh(paiement)
    
    # Envoyer notification au parent
    if etudiant.parent and etudiant.parent.telephone:
        envoyer_notification_paiement(db, paiement, etudiant)
    
    return {
        'success': True,
        'message': 'Paiement enregistre avec succes',
        'paiement': {
            'id': paiement.id,
            'reference': paiement.reference,
            'numero_recu': paiement.numero_recu,
            'montant': paiement.montant,
            'devise': paiement.devise,
            'frais': paiement.frais_transaction,
            'montant_net': paiement.montant_net,
            'statut': paiement.statut,
            'date': paiement.date_paiement.isoformat()
        }
    }

# ══════════════════════════════════════════════════════════════
# LISTE DES MOYENS DE PAIEMENT DISPONIBLES
# ══════════════════════════════════════════════════════════════

@router.get('/moyens-paiement')
def get_moyens_paiement(db: Session = Depends(get_db)):
    """Liste tous les moyens de paiement actifs"""
    
    configs = db.query(models.ConfigurationPaiement).filter(
        models.ConfigurationPaiement.actif == True,
        models.ConfigurationPaiement.visible == True
    ).order_by(models.ConfigurationPaiement.ordre_affichage).all()
    
    moyens = []
    for config in configs:
        moyens.append({
            'code': config.mode_paiement,
            'nom': config.nom_affichage,
            'description': config.description,
            'logo_url': config.logo_url,
            'couleur': config.couleur_hex,
            'icone': config.icone,
            'frais_pourcentage': config.frais_pourcentage,
            'frais_fixe': config.frais_fixe,
            'montant_min': config.montant_min,
            'montant_max': config.montant_max,
            'instructions': config.instructions
        })
    
    # Grouper par categorie
    return {
        'mobile_money': [m for m in moyens if m['code'] in ['mpesa', 'airtel_money', 'orange_money', 'afrimoney']],
        'agences': [m for m in moyens if m['code'] in ['western_union', 'moneygram', 'ria', 'worldremit']],
        'banques': [m for m in moyens if m['code'] in ['rawbank', 'equity_bank', 'tmb', 'sofibanque', 'ecobank', 'bgfi']],
        'autres': [m for m in moyens if m['code'] in ['especes', 'cheque', 'virement', 'carte_bancaire']]
    }

# ══════════════════════════════════════════════════════════════
# HISTORIQUE DES PAIEMENTS
# ══════════════════════════════════════════════════════════════

@router.get('/historique')
def get_historique_paiements(
    etudiant_id: Optional[int] = None,
    mode_paiement: Optional[str] = None,
    statut: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Historique des paiements avec filtres"""
    
    query = db.query(models.Paiement).filter(
        models.Paiement.ecole_id == current_user.ecole_id
    )
    
    if etudiant_id:
        query = query.filter(models.Paiement.etudiant_id == etudiant_id)
    if mode_paiement:
        query = query.filter(models.Paiement.mode_paiement == mode_paiement)
    if statut:
        query = query.filter(models.Paiement.statut == statut)
    if date_debut:
        query = query.filter(models.Paiement.date_paiement >= date_debut)
    if date_fin:
        query = query.filter(models.Paiement.date_paiement <= date_fin)
    
    total = query.count()
    paiements = query.order_by(
        models.Paiement.date_paiement.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        'total': total,
        'page': skip // limit + 1,
        'pages': (total + limit - 1) // limit,
        'paiements': [
            {
                'id': p.id,
                'reference': p.reference,
                'numero_recu': p.numero_recu,
                'etudiant': {
                    'nom': p.etudiant.nom,
                    'prenom': p.etudiant.prenom,
                    'matricule': p.etudiant.matricule,
                    'classe': p.etudiant.classe.nom if p.etudiant.classe else None
                },
                'montant': p.montant,
                'devise': p.devise,
                'type_frais': p.type_frais,
                'mode_paiement': p.mode_paiement,
                'statut': p.statut,
                'date': p.date_paiement.isoformat(),
                'enregistre_par': p.enregistre_par
            }
            for p in paiements
        ]
    }

# ══════════════════════════════════════════════════════════════
# DETAILS D'UN PAIEMENT
# ══════════════════════════════════════════════════════════════

@router.get('/{paiement_id}')
def get_paiement_details(
    paiement_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Details complets d'un paiement"""
    
    paiement = db.query(models.Paiement).filter(
        models.Paiement.id == paiement_id,
        models.Paiement.ecole_id == current_user.ecole_id
    ).first()
    
    if not paiement:
        raise HTTPException(404, 'Paiement introuvable')
    
    return {
        'id': paiement.id,
        'reference': paiement.reference,
        'numero_recu': paiement.numero_recu,
        'etudiant': {
            'id': paiement.etudiant.id,
            'nom': paiement.etudiant.nom,
            'prenom': paiement.etudiant.prenom,
            'matricule': paiement.etudiant.matricule,
            'classe': paiement.etudiant.classe.nom if paiement.etudiant.classe else None,
            'parent': {
                'nom': paiement.etudiant.parent.nom if paiement.etudiant.parent else None,
                'telephone': paiement.etudiant.parent.telephone if paiement.etudiant.parent else None
            }
        },
        'montant': paiement.montant,
        'devise': paiement.devise,
        'type_frais': paiement.type_frais,
        'description': paiement.description,
        'mode_paiement': paiement.mode_paiement,
        'statut': paiement.statut,
        'numero_transaction': paiement.numero_transaction,
        'numero_telephone': paiement.numero_telephone,
        'nom_expediteur': paiement.nom_expediteur,
        'code_mtcn': paiement.code_mtcn,
        'agence_nom': paiement.agence_nom,
        'numero_compte': paiement.numero_compte,
        'nom_banque': paiement.nom_banque,
        'numero_cheque': paiement.numero_cheque,
        'numero_bordereau': paiement.numero_bordereau,
        'frais_transaction': paiement.frais_transaction,
        'montant_net': paiement.montant_net,
        'date_paiement': paiement.date_paiement.isoformat(),
        'date_validation': paiement.date_validation.isoformat() if paiement.date_validation else None,
        'enregistre_par': paiement.enregistre_par,
        'valide_par': paiement.valide_par,
        'recu_url': paiement.recu_url,
        'notes': paiement.notes
    }

# ══════════════════════════════════════════════════════════════
# VALIDER UN PAIEMENT
# ══════════════════════════════════════════════════════════════

@router.put('/{paiement_id}/valider')
def valider_paiement(
    paiement_id: int,
    numero_transaction: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Valide un paiement en attente"""
    
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusee')
    
    paiement = db.query(models.Paiement).filter(
        models.Paiement.id == paiement_id,
        models.Paiement.ecole_id == current_user.ecole_id
    ).first()
    
    if not paiement:
        raise HTTPException(404, 'Paiement introuvable')
    
    paiement.statut = models.StatutPaiementEnum.VALIDE
    paiement.date_validation = datetime.utcnow()
    paiement.valide_par = current_user.id
    
    if numero_transaction:
        paiement.numero_transaction = numero_transaction
    if notes:
        paiement.notes_internes = notes
    
    db.commit()
    
    return {'success': True, 'message': 'Paiement valide'}

# ══════════════════════════════════════════════════════════════
# STATISTIQUES DES PAIEMENTS
# ══════════════════════════════════════════════════════════════

@router.get('/stats/dashboard')
def get_stats_paiements(
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Statistiques des paiements"""
    
    from sqlalchemy import func
    
    query = db.query(models.Paiement).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        models.Paiement.statut == models.StatutPaiementEnum.VALIDE
    )
    
    if date_debut:
        query = query.filter(models.Paiement.date_paiement >= date_debut)
    if date_fin:
        query = query.filter(models.Paiement.date_paiement <= date_fin)
    
    # Total par devise
    total_cdf = query.filter(models.Paiement.devise == 'CDF').with_entities(
        func.sum(models.Paiement.montant)
    ).scalar() or 0
    
    total_usd = query.filter(models.Paiement.devise == 'USD').with_entities(
        func.sum(models.Paiement.montant)
    ).scalar() or 0
    
    # Par mode de paiement
    par_mode = db.query(
        models.Paiement.mode_paiement,
        func.count(models.Paiement.id).label('nombre'),
        func.sum(models.Paiement.montant).label('total')
    ).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        models.Paiement.statut == models.StatutPaiementEnum.VALIDE
    ).group_by(models.Paiement.mode_paiement).all()
    
    return {
        'total_cdf': float(total_cdf),
        'total_usd': float(total_usd),
        'nombre_paiements': query.count(),
        'par_mode_paiement': [
            {
                'mode': p.mode_paiement,
                'nombre': p.nombre,
                'total': float(p.total or 0)
            }
            for p in par_mode
        ]
    }

# ══════════════════════════════════════════════════════════════
# FONCTION UTILITAIRE
# ══════════════════════════════════════════════════════════════

def envoyer_notification_paiement(db, paiement, etudiant):
    """Envoie une notification SMS au parent"""
    
    message = f"Paiement recu: {paiement.montant} {paiement.devise} pour {etudiant.prenom} {etudiant.nom}. Ref: {paiement.reference}. Merci! - Oasis des Juniors"
    
    notification = models.Notification(
        ecole_id=paiement.ecole_id,
        type='sms',
        destinataire=etudiant.parent.telephone,
        message=message,
        statut='en_attente',
        cout=0.05
    )
    db.add(notification)
    db.commit()

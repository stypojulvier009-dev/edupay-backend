from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db
import secrets
import requests

router = APIRouter(prefix='/api/mobile-money', tags=['Mobile Money RDC'])

# ══════════════════════════════════════════════════════════════
# INITIER UN PAIEMENT MOBILE MONEY
# ══════════════════════════════════════════════════════════════

@router.post('/initier-paiement')
def initier_paiement_mobile_money(
    etudiant_id: int,
    montant: float,
    operateur: str,  # mpesa, airtel_money, orange_money, afrimoney
    numero_telephone: str,  # +243XXXXXXXXX
    type_frais: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initie un paiement Mobile Money pour un etudiant
    Operateurs: M-Pesa, Airtel Money, Orange Money, AfriMoney
    """
    
    # Verifier l'etudiant
    etudiant = db.query(models.Etudiant).filter(
        models.Etudiant.id == etudiant_id,
        models.Etudiant.ecole_id == current_user.ecole_id
    ).first()
    if not etudiant:
        raise HTTPException(404, 'Etudiant introuvable')
    
    # Verifier la configuration de l'operateur
    config = db.query(models.ConfigurationMobileMoney).filter(
        models.ConfigurationMobileMoney.operateur == operateur,
        models.ConfigurationMobileMoney.actif == True
    ).first()
    if not config:
        raise HTTPException(400, f'Operateur {operateur} non configure ou inactif')
    
    # Verifier les limites
    if montant < config.montant_min:
        raise HTTPException(400, f'Montant minimum: {config.montant_min} CDF')
    if montant > config.montant_max:
        raise HTTPException(400, f'Montant maximum: {config.montant_max} CDF')
    
    # Calculer les frais
    frais_operateur = (montant * config.frais_pourcentage / 100) + config.frais_fixe
    commission_edupay = montant * 0.02  # 2% de commission EduPay
    montant_net = montant - frais_operateur - commission_edupay
    
    # Creer le paiement
    reference = f"OASIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
    
    paiement = models.Paiement(
        etudiant_id=etudiant_id,
        montant=montant,
        devise="CDF",
        type_frais=type_frais,
        statut=models.StatutPaiementEnum.EN_ATTENTE,
        mode_paiement=f"Mobile Money - {operateur.upper()}",
        reference=reference,
        utilisateur_id=current_user.id,
        ecole_id=current_user.ecole_id
    )
    db.add(paiement)
    db.flush()
    
    # Creer la transaction Mobile Money
    transaction_id = f"MM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(6).upper()}"
    
    transaction = models.TransactionMobileMoney(
        paiement_id=paiement.id,
        operateur=operateur,
        numero_telephone=numero_telephone,
        montant=montant,
        devise="CDF",
        transaction_id=transaction_id,
        statut=models.StatutTransactionEnum.EN_ATTENTE,
        frais_operateur=frais_operateur,
        commission_edupay=commission_edupay,
        montant_net=montant_net,
        date_expiration=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Appeler l'API de l'operateur (simulation)
    # En production, remplacer par les vraies API M-Pesa, Airtel, etc.
    resultat_api = appeler_api_operateur(config, transaction, numero_telephone, montant)
    
    if resultat_api['success']:
        transaction.statut = models.StatutTransactionEnum.EN_COURS
        transaction.reference_externe = resultat_api.get('reference')
        db.commit()
        
        return {
            'success': True,
            'message': f'Paiement initie. Composez *{get_code_ussd(operateur)}# pour confirmer',
            'transaction_id': transaction.transaction_id,
            'reference': reference,
            'montant': montant,
            'frais': frais_operateur,
            'montant_total': montant + frais_operateur,
            'expiration': transaction.date_expiration.isoformat()
        }
    else:
        transaction.statut = models.StatutTransactionEnum.ECHOUEE
        transaction.message_erreur = resultat_api.get('erreur')
        db.commit()
        raise HTTPException(400, resultat_api.get('erreur', 'Erreur lors de l\'initiation'))

# ══════════════════════════════════════════════════════════════
# VERIFIER LE STATUT D'UNE TRANSACTION
# ══════════════════════════════════════════════════════════════

@router.get('/statut/{transaction_id}')
def verifier_statut_transaction(
    transaction_id: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Verifie le statut d'une transaction Mobile Money"""
    
    transaction = db.query(models.TransactionMobileMoney).filter(
        models.TransactionMobileMoney.transaction_id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(404, 'Transaction introuvable')
    
    # Verifier si expiree
    if transaction.statut == models.StatutTransactionEnum.EN_ATTENTE:
        if datetime.utcnow() > transaction.date_expiration:
            transaction.statut = models.StatutTransactionEnum.ECHOUEE
            transaction.message_erreur = "Transaction expiree"
            db.commit()
    
    return {
        'transaction_id': transaction.transaction_id,
        'statut': transaction.statut,
        'operateur': transaction.operateur,
        'montant': transaction.montant,
        'numero_telephone': transaction.numero_telephone,
        'date_initiation': transaction.date_initiation.isoformat(),
        'date_completion': transaction.date_completion.isoformat() if transaction.date_completion else None,
        'message_erreur': transaction.message_erreur
    }

# ══════════════════════════════════════════════════════════════
# WEBHOOK POUR CALLBACKS DES OPERATEURS
# ══════════════════════════════════════════════════════════════

@router.post('/webhook/{operateur}')
def webhook_mobile_money(
    operateur: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Recoit les callbacks des operateurs Mobile Money
    M-Pesa, Airtel Money, Orange Money, AfriMoney
    """
    
    # Parser le payload selon l'operateur
    transaction_id = payload.get('transaction_id') or payload.get('TransID')
    statut = payload.get('status') or payload.get('ResultCode')
    
    transaction = db.query(models.TransactionMobileMoney).filter(
        models.TransactionMobileMoney.transaction_id == transaction_id
    ).first()
    
    if not transaction:
        return {'success': False, 'message': 'Transaction introuvable'}
    
    # Mettre a jour le statut
    if statut == '0' or statut == 'SUCCESS':
        transaction.statut = models.StatutTransactionEnum.REUSSIE
        transaction.date_completion = datetime.utcnow()
        
        # Mettre a jour le paiement
        paiement = db.query(models.Paiement).filter(
            models.Paiement.id == transaction.paiement_id
        ).first()
        if paiement:
            paiement.statut = models.StatutPaiementEnum.PAYE
            paiement.numero_transaction = transaction.reference_externe
            
            # Envoyer notification SMS au parent
            envoyer_notification_paiement(db, paiement, transaction)
    else:
        transaction.statut = models.StatutTransactionEnum.ECHOUEE
        transaction.code_erreur = str(statut)
        transaction.message_erreur = payload.get('message', 'Paiement echoue')
    
    transaction.webhook_reponse = str(payload)
    db.commit()
    
    return {'success': True, 'message': 'Webhook traite'}

# ══════════════════════════════════════════════════════════════
# LISTE DES OPERATEURS DISPONIBLES
# ══════════════════════════════════════════════════════════════

@router.get('/operateurs')
def get_operateurs_disponibles(db: Session = Depends(get_db)):
    """Liste des operateurs Mobile Money actifs"""
    
    configs = db.query(models.ConfigurationMobileMoney).filter(
        models.ConfigurationMobileMoney.actif == True
    ).order_by(models.ConfigurationMobileMoney.ordre_affichage).all()
    
    return [
        {
            'operateur': config.operateur,
            'nom': get_nom_operateur(config.operateur),
            'logo_url': config.logo_url,
            'couleur': config.couleur_hex,
            'montant_min': config.montant_min,
            'montant_max': config.montant_max,
            'frais_pourcentage': config.frais_pourcentage,
            'code_ussd': get_code_ussd(config.operateur)
        }
        for config in configs
    ]

# ══════════════════════════════════════════════════════════════
# HISTORIQUE TRANSACTIONS
# ══════════════════════════════════════════════════════════════

@router.get('/transactions')
def get_transactions_mobile_money(
    operateur: str = None,
    statut: str = None,
    date_debut: str = None,
    date_fin: str = None,
    skip: int = 0,
    limit: int = 50,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Historique des transactions Mobile Money"""
    
    query = db.query(models.TransactionMobileMoney).join(
        models.Paiement
    ).filter(
        models.Paiement.ecole_id == current_user.ecole_id
    )
    
    if operateur:
        query = query.filter(models.TransactionMobileMoney.operateur == operateur)
    if statut:
        query = query.filter(models.TransactionMobileMoney.statut == statut)
    if date_debut:
        query = query.filter(models.TransactionMobileMoney.date_initiation >= date_debut)
    if date_fin:
        query = query.filter(models.TransactionMobileMoney.date_initiation <= date_fin)
    
    transactions = query.order_by(
        models.TransactionMobileMoney.date_initiation.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        {
            'transaction_id': t.transaction_id,
            'operateur': t.operateur,
            'numero_telephone': t.numero_telephone,
            'montant': t.montant,
            'statut': t.statut,
            'date': t.date_initiation.isoformat(),
            'etudiant': {
                'nom': t.paiement.etudiant.nom,
                'prenom': t.paiement.etudiant.prenom,
                'matricule': t.paiement.etudiant.matricule
            }
        }
        for t in transactions
    ]

# ══════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════

def appeler_api_operateur(config, transaction, numero, montant):
    """Appelle l'API de l'operateur Mobile Money"""
    
    # SIMULATION - En production, remplacer par les vraies API
    if config.mode_test:
        return {
            'success': True,
            'reference': f"REF-{secrets.token_hex(8).upper()}",
            'message': 'Transaction initiee avec succes'
        }
    
    # Exemple pour M-Pesa (a adapter selon la vraie API)
    if config.operateur == 'mpesa':
        try:
            response = requests.post(
                f"{config.api_base_url}/payment",
                headers={
                    'Authorization': f'Bearer {config.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'phone': numero,
                    'amount': montant,
                    'reference': transaction.transaction_id,
                    'callback_url': config.callback_url
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'reference': data.get('reference'),
                    'message': 'Transaction initiee'
                }
        except Exception as e:
            return {'success': False, 'erreur': str(e)}
    
    return {'success': False, 'erreur': 'Operateur non supporte'}

def get_nom_operateur(operateur: str) -> str:
    noms = {
        'mpesa': 'Vodacom M-Pesa',
        'airtel_money': 'Airtel Money',
        'orange_money': 'Orange Money',
        'afrimoney': 'Africell AfriMoney'
    }
    return noms.get(operateur, operateur)

def get_code_ussd(operateur: str) -> str:
    codes = {
        'mpesa': '150',
        'airtel_money': '501',
        'orange_money': '144',
        'afrimoney': '555'
    }
    return codes.get(operateur, '000')

def envoyer_notification_paiement(db, paiement, transaction):
    """Envoie une notification SMS au parent"""
    
    if paiement.etudiant.parent and paiement.etudiant.parent.telephone:
        message = f"Paiement recu: {transaction.montant} CDF pour {paiement.etudiant.prenom} {paiement.etudiant.nom}. Ref: {paiement.reference}. Merci! - Oasis des Juniors"
        
        notification = models.Notification(
            ecole_id=paiement.ecole_id,
            type='sms',
            destinataire=paiement.etudiant.parent.telephone,
            message=message,
            statut='en_attente',
            cout=0.05  # 5 cents par SMS
        )
        db.add(notification)
        db.commit()

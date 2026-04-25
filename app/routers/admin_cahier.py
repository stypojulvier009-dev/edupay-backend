from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db
import io
import csv

router = APIRouter(prefix='/api/admin/cahier-paiements', tags=['Admin - Cahier Paiements'])

# ══════════════════════════════════════════════════════════════
# CAHIER DE PAIEMENTS (REGISTRE JOURNALIER)
# ══════════════════════════════════════════════════════════════

@router.get('/registre/{date}')
def get_registre_journalier(
    date: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Registre des paiements du jour"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    from sqlalchemy import func
    
    # Récupérer tous les paiements du jour
    paiements = db.query(models.Paiement).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        func.date(models.Paiement.date_paiement) == date
    ).all()
    
    # Calculer les totaux par mode de paiement
    total_especes = sum(p.montant for p in paiements if p.mode_paiement == 'especes')
    total_mobile_money = sum(p.montant for p in paiements if p.mode_paiement in ['mpesa', 'airtel_money', 'orange_money', 'afrimoney'])
    total_banque = sum(p.montant for p in paiements if p.mode_paiement in ['rawbank', 'equity_bank', 'tmb', 'sofibanque', 'ecobank', 'bgfi'])
    total_agence = sum(p.montant for p in paiements if p.mode_paiement in ['western_union', 'moneygram', 'ria', 'worldremit'])
    total_general = sum(p.montant for p in paiements)
    
    # Vérifier si le registre existe
    registre = db.query(models.RegistrePaiement).filter(
        func.date(models.RegistrePaiement.date) == date
    ).first()
    
    if not registre:
        registre = models.RegistrePaiement(
            date=date,
            total_especes=total_especes,
            total_mobile_money=total_mobile_money,
            total_banque=total_banque,
            total_agence=total_agence,
            total_general=total_general,
            nombre_transactions=len(paiements)
        )
        db.add(registre)
        db.commit()
        db.refresh(registre)
    
    return {
        'date': date,
        'registre': {
            'id': registre.id,
            'total_especes': total_especes,
            'total_mobile_money': total_mobile_money,
            'total_banque': total_banque,
            'total_agence': total_agence,
            'total_general': total_general,
            'nombre_transactions': len(paiements),
            'verifie': registre.verifie,
            'cloture': registre.cloture
        },
        'paiements': [
            {
                'id': p.id,
                'reference': p.reference,
                'numero_recu': p.numero_recu,
                'etudiant': f"{p.etudiant.prenom} {p.etudiant.nom}",
                'matricule': p.etudiant.matricule,
                'classe': p.etudiant.classe.nom if p.etudiant.classe else None,
                'type_frais': p.type_frais,
                'montant': p.montant,
                'devise': p.devise,
                'mode_paiement': p.mode_paiement,
                'heure': p.date_paiement.strftime('%H:%M'),
                'enregistre_par': p.enregistre_par
            }
            for p in paiements
        ]
    }

@router.put('/registre/{registre_id}/verifier')
def verifier_registre(
    registre_id: int,
    observations: str = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Vérifier le registre journalier"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    registre = db.query(models.RegistrePaiement).filter(
        models.RegistrePaiement.id == registre_id
    ).first()
    if not registre:
        raise HTTPException(404, 'Registre introuvable')
    
    registre.verifie = True
    registre.verifie_par = current_user.id
    registre.date_verification = datetime.utcnow()
    if observations:
        registre.observations = observations
    
    db.commit()
    return {'success': True, 'message': 'Registre vérifié'}

@router.put('/registre/{registre_id}/cloturer')
def cloturer_registre(
    registre_id: int,
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Clôturer le registre journalier"""
    registre = db.query(models.RegistrePaiement).filter(
        models.RegistrePaiement.id == registre_id
    ).first()
    if not registre:
        raise HTTPException(404, 'Registre introuvable')
    
    if not registre.verifie:
        raise HTTPException(400, 'Le registre doit être vérifié avant clôture')
    
    registre.cloture = True
    registre.cloture_par = current_user.id
    registre.date_cloture = datetime.utcnow()
    
    db.commit()
    return {'success': True, 'message': 'Registre clôturé'}

# ══════════════════════════════════════════════════════════════
# EXPORTS ET TELECHARGEMENTS
# ══════════════════════════════════════════════════════════════

@router.get('/export/paiements-csv')
def export_paiements_csv(
    date_debut: str,
    date_fin: str,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger tous les paiements en CSV"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur', 'comptable']:
        raise HTTPException(403, 'Permission refusée')
    
    paiements = db.query(models.Paiement).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        models.Paiement.date_paiement >= date_debut,
        models.Paiement.date_paiement <= date_fin
    ).all()
    
    # Créer le CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow([
        'Date', 'Référence', 'N° Reçu', 'Matricule', 'Nom', 'Prénom', 
        'Classe', 'Type Frais', 'Montant', 'Devise', 'Mode Paiement', 
        'Statut', 'Enregistré par'
    ])
    
    # Données
    for p in paiements:
        writer.writerow([
            p.date_paiement.strftime('%Y-%m-%d %H:%M'),
            p.reference,
            p.numero_recu,
            p.etudiant.matricule,
            p.etudiant.nom,
            p.etudiant.prenom,
            p.etudiant.classe.nom if p.etudiant.classe else '',
            p.type_frais,
            p.montant,
            p.devise,
            p.mode_paiement,
            p.statut,
            p.enregistre_par
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=paiements_{date_debut}_{date_fin}.csv'
        }
    )

@router.get('/export/etudiants-csv')
def export_etudiants_csv(
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger la liste des étudiants en CSV"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    etudiants = db.query(models.Etudiant).filter(
        models.Etudiant.ecole_id == current_user.ecole_id
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Matricule', 'Nom', 'Prénom', 'Date Naissance', 'Sexe',
        'Classe', 'Parent', 'Téléphone Parent', 'Boursier', 'Actif'
    ])
    
    for e in etudiants:
        writer.writerow([
            e.matricule,
            e.nom,
            e.prenom,
            e.date_naissance.strftime('%Y-%m-%d') if e.date_naissance else '',
            e.sexe,
            e.classe.nom if e.classe else '',
            f"{e.parent.prenom} {e.parent.nom}" if e.parent else '',
            e.parent.telephone if e.parent else '',
            'Oui' if e.boursier else 'Non',
            'Oui' if e.actif else 'Non'
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=etudiants.csv'
        }
    )

@router.get('/export/presences-csv')
def export_presences_csv(
    date_debut: str,
    date_fin: str,
    classe_id: int = None,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger les présences en CSV"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    query = db.query(models.Presence).filter(
        models.Presence.date >= date_debut,
        models.Presence.date <= date_fin
    )
    
    if classe_id:
        query = query.filter(models.Presence.classe_id == classe_id)
    
    presences = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Date', 'Matricule', 'Nom', 'Prénom', 'Classe',
        'Présent', 'Retard', 'Justifié', 'Motif'
    ])
    
    for p in presences:
        writer.writerow([
            p.date.strftime('%Y-%m-%d'),
            p.etudiant.matricule,
            p.etudiant.nom,
            p.etudiant.prenom,
            p.classe.nom,
            'Oui' if p.present else 'Non',
            'Oui' if p.retard else 'Non',
            'Oui' if p.justifie else 'Non',
            p.motif_absence or ''
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=presences_{date_debut}_{date_fin}.csv'
        }
    )

@router.get('/export/notes-csv')
def export_notes_csv(
    classe_id: int,
    trimestre: int,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger les notes en CSV"""
    if current_user.role not in ['super_admin', 'admin_ecole', 'directeur']:
        raise HTTPException(403, 'Permission refusée')
    
    # Récupérer tous les examens de la classe
    examens = db.query(models.Examen).filter(
        models.Examen.classe_id == classe_id
    ).all()
    
    # Récupérer tous les étudiants
    etudiants = db.query(models.Etudiant).filter(
        models.Etudiant.classe_id == classe_id
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    headers = ['Matricule', 'Nom', 'Prénom']
    for examen in examens:
        headers.append(f"{examen.matiere.nom} - {examen.titre}")
    headers.append('Moyenne')
    writer.writerow(headers)
    
    # Données
    for etudiant in etudiants:
        row = [etudiant.matricule, etudiant.nom, etudiant.prenom]
        total_notes = 0
        count_notes = 0
        
        for examen in examens:
            note = db.query(models.Note).filter(
                models.Note.examen_id == examen.id,
                models.Note.etudiant_id == etudiant.id
            ).first()
            
            if note and not note.absent:
                row.append(note.note)
                total_notes += note.note
                count_notes += 1
            else:
                row.append('Absent' if note and note.absent else '')
        
        moyenne = total_notes / count_notes if count_notes > 0 else 0
        row.append(round(moyenne, 2))
        writer.writerow(row)
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=notes_classe_{classe_id}_trimestre_{trimestre}.csv'
        }
    )

@router.get('/stats/globales')
def get_stats_globales(
    current_user: models.Utilisateur = Depends(auth.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Statistiques globales de l'école"""
    from sqlalchemy import func
    
    total_etudiants = db.query(models.Etudiant).filter(
        models.Etudiant.ecole_id == current_user.ecole_id,
        models.Etudiant.actif == True
    ).count()
    
    total_paiements = db.query(func.sum(models.Paiement.montant)).filter(
        models.Paiement.ecole_id == current_user.ecole_id,
        models.Paiement.statut == 'valide'
    ).scalar() or 0
    
    total_utilisateurs = db.query(models.Utilisateur).filter(
        models.Utilisateur.ecole_id == current_user.ecole_id,
        models.Utilisateur.actif == True
    ).count()
    
    total_classes = db.query(models.Classe).filter(
        models.Classe.ecole_id == current_user.ecole_id
    ).count()
    
    return {
        'etudiants': {
            'total': total_etudiants,
            'actifs': total_etudiants
        },
        'paiements': {
            'total': float(total_paiements),
            'nombre': db.query(models.Paiement).filter(
                models.Paiement.ecole_id == current_user.ecole_id
            ).count()
        },
        'utilisateurs': {
            'total': total_utilisateurs
        },
        'classes': {
            'total': total_classes
        }
    }

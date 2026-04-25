# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash
from datetime import datetime

def init_oasis_des_juniors():
    """Initialise la base de donnees complete pour Oasis des Juniors"""
    
    # Creer les tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=== INITIALISATION OASIS DES JUNIORS COMPLETE ===\n")
        
        # 1. CREER L'ECOLE
        print("1. Creation de l'ecole...")
        ecole = models.Ecole(
            nom="Complexe Scolaire Oasis des Juniors",
            code="OASIS001",
            type="Primaire et Secondaire",
            adresse="Lubumbashi, RDC",
            telephone="+243999999999",
            email="contact@oasisdesjuniors.cd",
            directeur_nom="Directeur Oasis",
            capacite_eleves=1000,
            annee_creation=2020,
            actif=True
        )
        db.add(ecole)
        db.flush()
        print(f"   Ecole: {ecole.nom}")
        
        # 2. UTILISATEURS
        print("\n2. Creation des utilisateurs...")
        admin = models.Utilisateur(
            nom="Admin", prenom="Oasis",
            email="admin@oasisdesjuniors.cd",
            telephone="+243999999999",
            mot_de_passe_hash=get_password_hash("Admin123!"),
            role=models.RoleEnum.SUPER_ADMIN,
            ecole_id=ecole.id, actif=True
        )
        db.add(admin)
        print("   - Admin: admin@oasisdesjuniors.cd / Admin123!")
        
        directeur = models.Utilisateur(
            nom="Directeur", prenom="Oasis",
            email="directeur@oasisdesjuniors.cd",
            telephone="+243999999998",
            mot_de_passe_hash=get_password_hash("Directeur123!"),
            role=models.RoleEnum.DIRECTEUR,
            ecole_id=ecole.id, actif=True
        )
        db.add(directeur)
        print("   - Directeur: directeur@oasisdesjuniors.cd / Directeur123!")
        
        comptable = models.Utilisateur(
            nom="Comptable", prenom="Oasis",
            email="comptable@oasisdesjuniors.cd",
            telephone="+243999999997",
            mot_de_passe_hash=get_password_hash("Comptable123!"),
            role=models.RoleEnum.COMPTABLE,
            ecole_id=ecole.id, actif=True
        )
        db.add(comptable)
        print("   - Comptable: comptable@oasisdesjuniors.cd / Comptable123!")
        
        caissier = models.Utilisateur(
            nom="Caissier", prenom="Oasis",
            email="caissier@oasisdesjuniors.cd",
            telephone="+243999999996",
            mot_de_passe_hash=get_password_hash("Caissier123!"),
            role=models.RoleEnum.CAISSIER,
            ecole_id=ecole.id, actif=True
        )
        db.add(caissier)
        print("   - Caissier: caissier@oasisdesjuniors.cd / Caissier123!")
        db.flush()
        
        # 3. CLASSES
        print("\n3. Creation des classes...")
        classes_data = [
            {"nom": "1ere Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "2eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "3eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "4eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "5eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "6eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "7eme Annee", "niveau": "Secondaire", "capacite": 50},
            {"nom": "8eme Annee", "niveau": "Secondaire", "capacite": 50},
            {"nom": "1ere Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "2eme Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "3eme Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "4eme Secondaire", "niveau": "Secondaire", "capacite": 50},
        ]
        for c in classes_data:
            classe = models.Classe(**c, ecole_id=ecole.id, annee_scolaire="2024-2025")
            db.add(classe)
            print(f"   - {c['nom']}")
        db.flush()
        
        # 4. FRAIS SCOLAIRES
        print("\n4. Configuration des frais...")
        frais_data = [
            {"nom": "Frais d'inscription", "montant": 50000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 1er trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 2eme trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 3eme trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Frais d'examen", "montant": 30000, "devise": "CDF", "obligatoire": True},
            {"nom": "Uniforme scolaire", "montant": 40000, "devise": "CDF", "obligatoire": False},
            {"nom": "Fournitures scolaires", "montant": 25000, "devise": "CDF", "obligatoire": False},
        ]
        for f in frais_data:
            frais = models.FraisScolaire(**f, ecole_id=ecole.id, annee_scolaire="2024-2025")
            db.add(frais)
            print(f"   - {f['nom']}: {f['montant']} CDF")
        db.flush()
        
        # 5. CONFIGURATION MOYENS DE PAIEMENT (20+)
        print("\n5. Configuration moyens de paiement RDC...")
        moyens = [
            # Mobile Money
            {"mode_paiement": "mpesa", "nom_affichage": "Vodacom M-Pesa", "actif": True, "visible": True, "frais_pourcentage": 2.0, "montant_min": 100, "ordre_affichage": 1},
            {"mode_paiement": "airtel_money", "nom_affichage": "Airtel Money", "actif": True, "visible": True, "frais_pourcentage": 2.0, "montant_min": 100, "ordre_affichage": 2},
            {"mode_paiement": "orange_money", "nom_affichage": "Orange Money", "actif": True, "visible": True, "frais_pourcentage": 2.0, "montant_min": 100, "ordre_affichage": 3},
            {"mode_paiement": "afrimoney", "nom_affichage": "Africell AfriMoney", "actif": True, "visible": True, "frais_pourcentage": 2.0, "montant_min": 100, "ordre_affichage": 4},
            # Agences
            {"mode_paiement": "western_union", "nom_affichage": "Western Union", "actif": True, "visible": True, "frais_pourcentage": 3.0, "ordre_affichage": 5},
            {"mode_paiement": "moneygram", "nom_affichage": "MoneyGram", "actif": True, "visible": True, "frais_pourcentage": 3.0, "ordre_affichage": 6},
            {"mode_paiement": "ria", "nom_affichage": "Ria Money Transfer", "actif": True, "visible": True, "frais_pourcentage": 3.0, "ordre_affichage": 7},
            {"mode_paiement": "worldremit", "nom_affichage": "WorldRemit", "actif": True, "visible": True, "frais_pourcentage": 3.0, "ordre_affichage": 8},
            # Banques
            {"mode_paiement": "rawbank", "nom_affichage": "Rawbank", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 9},
            {"mode_paiement": "equity_bank", "nom_affichage": "Equity Bank", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 10},
            {"mode_paiement": "tmb", "nom_affichage": "Trust Merchant Bank", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 11},
            {"mode_paiement": "sofibanque", "nom_affichage": "Sofibanque", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 12},
            {"mode_paiement": "ecobank", "nom_affichage": "Ecobank", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 13},
            {"mode_paiement": "bgfi", "nom_affichage": "BGFI Bank", "actif": True, "visible": True, "frais_pourcentage": 1.0, "ordre_affichage": 14},
            # Autres
            {"mode_paiement": "especes", "nom_affichage": "Espèces", "actif": True, "visible": True, "frais_pourcentage": 0.0, "ordre_affichage": 15},
            {"mode_paiement": "cheque", "nom_affichage": "Chèque", "actif": True, "visible": True, "frais_pourcentage": 0.0, "ordre_affichage": 16},
            {"mode_paiement": "virement", "nom_affichage": "Virement", "actif": True, "visible": True, "frais_pourcentage": 0.5, "ordre_affichage": 17},
            {"mode_paiement": "carte_bancaire", "nom_affichage": "Carte Bancaire", "actif": True, "visible": True, "frais_pourcentage": 2.5, "ordre_affichage": 18},
        ]
        for m in moyens:
            config = models.ConfigurationPaiement(**m)
            db.add(config)
        print("   - 18 moyens de paiement configures")
        db.flush()
        
        # 6. MATIERES
        print("\n6. Creation des matieres...")
        matieres_data = [
            {"nom": "Français", "code": "FR", "coefficient": 3.0},
            {"nom": "Mathématiques", "code": "MATH", "coefficient": 3.0},
            {"nom": "Sciences", "code": "SCI", "coefficient": 2.0},
            {"nom": "Histoire", "code": "HIST", "coefficient": 2.0},
            {"nom": "Géographie", "code": "GEO", "coefficient": 2.0},
            {"nom": "Anglais", "code": "ANG", "coefficient": 2.0},
            {"nom": "Education Physique", "code": "EP", "coefficient": 1.0},
        ]
        for mat in matieres_data:
            matiere = models.Matiere(**mat, ecole_id=ecole.id)
            db.add(matiere)
            print(f"   - {mat['nom']}")
        db.flush()
        
        db.commit()
        
        print("\n" + "="*60)
        print("INITIALISATION TERMINEE!")
        print("="*60)
        print("\nECOLE: Complexe Scolaire Oasis des Juniors")
        print("\nCOMPTES:")
        print("- Admin: admin@oasisdesjuniors.cd / Admin123!")
        print("- Directeur: directeur@oasisdesjuniors.cd / Directeur123!")
        print("- Comptable: comptable@oasisdesjuniors.cd / Comptable123!")
        print("- Caissier: caissier@oasisdesjuniors.cd / Caissier123!")
        print("\nCONFIGURATION:")
        print("- 12 classes (6 primaire + 6 secondaire)")
        print("- 7 types de frais")
        print("- 18 moyens de paiement RDC")
        print("- 7 matieres")
        print("\nFONCTIONNALITES:")
        print("- Gestion utilisateurs")
        print("- Presences et absences")
        print("- Journal de classe")
        print("- Cours et emploi du temps")
        print("- Examens et notes")
        print("- Cahier de paiements")
        print("- Exports CSV")
        print("- Internet obligatoire")
        print("\nAPI: http://localhost:8000/docs")
        print("="*60)
        
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_oasis_des_juniors()

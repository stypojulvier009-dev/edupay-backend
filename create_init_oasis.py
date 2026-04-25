# -*- coding: utf-8 -*-
"""
Script d'initialisation pour Complexe Scolaire Oasis des Juniors
Application DEDIEE (pas multi-tenant)
"""

init_oasis = '''
# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash
from datetime import datetime

def init_oasis_des_juniors():
    """Initialise la base de donnees pour Oasis des Juniors"""
    
    # Creer les tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=== INITIALISATION OASIS DES JUNIORS ===\\n")
        
        # 1. CREER L'ECOLE UNIQUE
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
        print(f"   Ecole creee: {ecole.nom} (ID: {ecole.id})")
        
        # 2. CREER LES UTILISATEURS
        print("\\n2. Creation des utilisateurs...")
        
        # Super Admin
        admin = models.Utilisateur(
            nom="Admin",
            prenom="Oasis",
            email="admin@oasisdesjuniors.cd",
            telephone="+243999999999",
            mot_de_passe_hash=get_password_hash("Admin123!"),
            role=models.RoleEnum.SUPER_ADMIN,
            ecole_id=ecole.id,
            actif=True
        )
        db.add(admin)
        print("   - Super Admin: admin@oasisdesjuniors.cd / Admin123!")
        
        # Directeur
        directeur = models.Utilisateur(
            nom="Directeur",
            prenom="Oasis",
            email="directeur@oasisdesjuniors.cd",
            telephone="+243999999998",
            mot_de_passe_hash=get_password_hash("Directeur123!"),
            role=models.RoleEnum.DIRECTEUR,
            ecole_id=ecole.id,
            actif=True
        )
        db.add(directeur)
        print("   - Directeur: directeur@oasisdesjuniors.cd / Directeur123!")
        
        # Comptable
        comptable = models.Utilisateur(
            nom="Comptable",
            prenom="Oasis",
            email="comptable@oasisdesjuniors.cd",
            telephone="+243999999997",
            mot_de_passe_hash=get_password_hash("Comptable123!"),
            role=models.RoleEnum.COMPTABLE,
            ecole_id=ecole.id,
            actif=True
        )
        db.add(comptable)
        print("   - Comptable: comptable@oasisdesjuniors.cd / Comptable123!")
        
        # Caissier
        caissier = models.Utilisateur(
            nom="Caissier",
            prenom="Oasis",
            email="caissier@oasisdesjuniors.cd",
            telephone="+243999999996",
            mot_de_passe_hash=get_password_hash("Caissier123!"),
            role=models.RoleEnum.CAISSIER,
            ecole_id=ecole.id,
            actif=True
        )
        db.add(caissier)
        print("   - Caissier: caissier@oasisdesjuniors.cd / Caissier123!")
        
        db.flush()
        
        # 3. CREER LES CLASSES
        print("\\n3. Creation des classes...")
        classes_data = [
            # Primaire
            {"nom": "1ere Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "2eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "3eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "4eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "5eme Primaire", "niveau": "Primaire", "capacite": 40},
            {"nom": "6eme Primaire", "niveau": "Primaire", "capacite": 40},
            # Secondaire
            {"nom": "7eme Annee", "niveau": "Secondaire", "capacite": 50},
            {"nom": "8eme Annee", "niveau": "Secondaire", "capacite": 50},
            {"nom": "1ere Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "2eme Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "3eme Secondaire", "niveau": "Secondaire", "capacite": 50},
            {"nom": "4eme Secondaire", "niveau": "Secondaire", "capacite": 50},
        ]
        
        for classe_data in classes_data:
            classe = models.Classe(
                **classe_data,
                ecole_id=ecole.id,
                annee_scolaire="2024-2025"
            )
            db.add(classe)
            print(f"   - {classe_data['nom']}")
        
        db.flush()
        
        # 4. CREER LES FRAIS SCOLAIRES
        print("\\n4. Configuration des frais scolaires...")
        frais_data = [
            {"nom": "Frais d'inscription", "montant": 50000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 1er trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 2eme trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Minerval 3eme trimestre", "montant": 150000, "devise": "CDF", "obligatoire": True},
            {"nom": "Frais d'examen", "montant": 30000, "devise": "CDF", "obligatoire": True},
            {"nom": "Uniforme scolaire", "montant": 40000, "devise": "CDF", "obligatoire": False},
            {"nom": "Fournitures scolaires", "montant": 25000, "devise": "CDF", "obligatoire": False},
        ]
        
        for frais_info in frais_data:
            frais = models.FraisScolaire(
                **frais_info,
                ecole_id=ecole.id,
                annee_scolaire="2024-2025"
            )
            db.add(frais)
            print(f"   - {frais_info['nom']}: {frais_info['montant']} {frais_info['devise']}")
        
        db.flush()
        
        # 5. CONFIGURER MOBILE MONEY RDC
        print("\\n5. Configuration Mobile Money RDC...")
        operateurs = [
            {
                "operateur": models.OperateurMobileMoneyEnum.MPESA,
                "merchant_name": "Oasis des Juniors",
                "actif": True,
                "mode_test": True,
                "frais_pourcentage": 2.0,
                "montant_min": 100.0,
                "montant_max": 5000000.0,
                "logo_url": "/static/logos/mpesa.png",
                "couleur_hex": "#E30613",
                "ordre_affichage": 1
            },
            {
                "operateur": models.OperateurMobileMoneyEnum.AIRTEL_MONEY,
                "merchant_name": "Oasis des Juniors",
                "actif": True,
                "mode_test": True,
                "frais_pourcentage": 2.0,
                "montant_min": 100.0,
                "montant_max": 5000000.0,
                "logo_url": "/static/logos/airtel.png",
                "couleur_hex": "#ED1C24",
                "ordre_affichage": 2
            },
            {
                "operateur": models.OperateurMobileMoneyEnum.ORANGE_MONEY,
                "merchant_name": "Oasis des Juniors",
                "actif": True,
                "mode_test": True,
                "frais_pourcentage": 2.0,
                "montant_min": 100.0,
                "montant_max": 5000000.0,
                "logo_url": "/static/logos/orange.png",
                "couleur_hex": "#FF7900",
                "ordre_affichage": 3
            },
            {
                "operateur": models.OperateurMobileMoneyEnum.AFRIMONEY,
                "merchant_name": "Oasis des Juniors",
                "actif": True,
                "mode_test": True,
                "frais_pourcentage": 2.0,
                "montant_min": 100.0,
                "montant_max": 5000000.0,
                "logo_url": "/static/logos/africell.png",
                "couleur_hex": "#0066CC",
                "ordre_affichage": 4
            }
        ]
        
        for op_data in operateurs:
            config = models.ConfigurationMobileMoney(**op_data)
            db.add(config)
            print(f"   - {op_data['operateur'].value.upper()}: Active")
        
        db.commit()
        
        print("\\n" + "="*50)
        print("INITIALISATION TERMINEE!")
        print("="*50)
        print("\\nECOLE: Complexe Scolaire Oasis des Juniors")
        print("\\nCOMPTES UTILISATEURS:")
        print("- Admin: admin@oasisdesjuniors.cd / Admin123!")
        print("- Directeur: directeur@oasisdesjuniors.cd / Directeur123!")
        print("- Comptable: comptable@oasisdesjuniors.cd / Comptable123!")
        print("- Caissier: caissier@oasisdesjuniors.cd / Caissier123!")
        print("\\nMOBILE MONEY RDC:")
        print("- Vodacom M-Pesa: Active")
        print("- Airtel Money: Active")
        print("- Orange Money: Active")
        print("- Africell AfriMoney: Active")
        print("\\nCLASSES: 12 classes (6 primaire + 6 secondaire)")
        print("FRAIS: 7 types de frais configures")
        print("\\nAPI: http://localhost:8000/docs")
        print("="*50)
        
    except Exception as e:
        print(f"\\nERREUR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_oasis_des_juniors()
'''

with open(r'E:\mon app\edupay\backend\app\init_oasis.py', 'w', encoding='utf-8') as f:
    f.write(init_oasis)

print("Script d'initialisation Oasis des Juniors cree!")
print("\nPour initialiser:")
print("python -m app.init_oasis")

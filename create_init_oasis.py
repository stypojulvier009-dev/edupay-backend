# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def init_my_admin():
    """Initialise la base et crée UNIQUEMENT le compte super admin personnel"""
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Vérifier si l'école existe, sinon la créer
        ecole = db.query(models.Ecole).filter(models.Ecole.code == "OASIS001").first()
        if not ecole:
            ecole = models.Ecole(
                nom="Complexe Scolaire Oasis des Juniors",
                code="OASIS001",
                type="Primaire et Secondaire",
                adresse="Lubumbashi, RDC",
                telephone="+243994477720",
                email="stypojulvier009@mail.com",
                directeur_nom="MUKENDI TDHITUKA JULVIER",
                capacite_eleves=1000,
                actif=True
            )
            db.add(ecole)
            db.flush()
            print("✅ École Oasis des Juniors créée")

        # Créer ou mettre à jour le super admin personnel
        email = "stypojulvier009@mail.com"
        user = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
        if user:
            user.role = models.RoleEnum.SUPER_ADMIN
            user.hashed_password = get_password_hash("2003")
            user.actif = True
            user.nom = "Administrateur"
            user.prenom = "Principal"
            user.ecole_id = ecole.id
            print("✅ Compte existant mis à jour en super admin")
        else:
            admin = models.Utilisateur(
                nom="Administrateur",
                prenom="Principal",
                email=email,
                hashed_password=get_password_hash("2003"),
                role=models.RoleEnum.SUPER_ADMIN,
                ecole_id=ecole.id,
                actif=True
            )
            db.add(admin)
            print("✅ Compte super admin créé")
        db.commit()
        print(f"\n🎉 Compte prêt : {email} / 2003")
    except Exception as e:
        print(f"Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_my_admin()

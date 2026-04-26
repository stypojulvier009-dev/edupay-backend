# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

def init_my_admin():
    """Crée uniquement le compte super admin stypojulvier009@mail.com"""
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = "stypojulvier009@mail.com"
        user = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
        if user:
            print(f"Compte existant, mise à jour en super_admin.")
            user.role = models.RoleEnum.SUPER_ADMIN
            user.hashed_password = get_password_hash("2003")
            user.actif = True
        else:
            admin = models.Utilisateur(
                nom="Administrateur",
                prenom="Principal",
                email=email,
                hashed_password=get_password_hash("2003"),
                role=models.RoleEnum.SUPER_ADMIN,
                actif=True
            )
            db.add(admin)
            print("Compte super admin créé.")
        db.commit()
        print("✅ Ton compte admin est prêt : stypojulvier009@mail.com / 2003")
    except Exception as e:
        print(f"Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_my_admin()

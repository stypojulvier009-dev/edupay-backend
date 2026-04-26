# Endpoint temporaire pour créer le super admin (à supprimer après usage)
@router.post('/create-super-admin')
def create_super_admin(db: Session = Depends(get_db)):
    email = "stypojulvier009@mail.com"
    user = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
    if not user:
        admin = models.Utilisateur(
            nom="Administrateur",
            prenom="Principal",
            email=email,
            hashed_password=get_password_hash("2003"),
            role=models.RoleEnum.SUPER_ADMIN,
            actif=True
        )
        db.add(admin)
        db.commit()
        return {"message": "✅ Super admin créé avec succès"}
    return {"message": "⚠️ Le super admin existe déjà"}

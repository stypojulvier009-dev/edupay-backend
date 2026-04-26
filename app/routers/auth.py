from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/auth', tags=['Authentification'])

# ========== INSCRIPTION PUBLIQUE DÉSACTIVÉE ==========
# On commente ou supprime l'endpoint /register
# Si vous voulez absolument le garder pour un usage interne, ajoutez une dépendance admin.

# @router.post('/register', response_model=schemas.UtilisateurOut)
# def register(...):
#     ...

@router.post('/login')
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == form_data.username
    ).first()
    
    if not user or not auth.verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email ou mot de passe incorrect',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    if not user.actif:
        raise HTTPException(400, 'Compte désactivé')
    
    access_token = auth.create_access_token(
        data={'sub': user.email, 'role': user.role}
    )
    
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email,
            'role': user.role,
            'ecole_id': user.ecole_id
        }
    }

@router.get('/me', response_model=schemas.UtilisateurOut)
def get_current_user_info(
    current_user: models.Utilisateur = Depends(auth.get_current_user)
):
    return current_user

@router.put('/me', response_model=schemas.UtilisateurOut)
def update_current_user(
    user_update: schemas.UtilisateurCreate,
    current_user: models.Utilisateur = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    for key, value in user_update.dict(exclude_unset=True, exclude={'mot_de_passe'}).items():
        setattr(current_user, key, value)
    
    if user_update.mot_de_passe:
        current_user.mot_de_passe_hash = auth.get_password_hash(user_update.mot_de_passe)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# ========== ENDPOINTS ADMIN POUR GÉRER LES UTILISATEURS ==========
# Fonction de vérification du rôle super admin
def require_super_admin(current_user: models.Utilisateur = Depends(auth.get_current_user)):
    if current_user.role != models.RoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Accès réservé au super administrateur")
    return current_user

@router.post('/admin/create-user')
def create_user_by_admin(
    user_data: schemas.UtilisateurCreate,
    db: Session = Depends(get_db),
    _=Depends(require_super_admin)
):
    # Vérifier si l'email existe déjà
    existing = db.query(models.Utilisateur).filter(models.Utilisateur.email == user_data.email).first()
    if existing:
        raise HTTPException(400, "Un utilisateur avec cet email existe déjà")
    
    hashed = auth.get_password_hash(user_data.mot_de_passe)
    new_user = models.Utilisateur(
        nom=user_data.nom,
        prenom=user_data.prenom,
        email=user_data.email,
        telephone=user_data.telephone,
        mot_de_passe_hash=hashed,
        role=user_data.role,
        ecole_id=user_data.ecole_id,
        actif=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"Utilisateur {new_user.email} créé", "user": new_user}

@router.delete('/admin/delete-user/{user_id}')
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_super_admin)
):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")
    # Empêcher la suppression de son propre compte (optionnel)
    # if user.email == "stypojulvier009@mail.com":
    #     raise HTTPException(400, "Vous ne pouvez pas supprimer votre propre compte")
    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user.email} supprimé"}

@router.put('/admin/block-user/{user_id}')
def block_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_super_admin)
):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")
    user.actif = not user.actif
    db.commit()
    status = "bloqué" if not user.actif else "débloqué"
    return {"message": f"Utilisateur {user.email} {status}"}

@router.post('/admin/logout-user/{user_id}')
def logout_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_super_admin)
):
    # Implémenter la révocation de token si nécessaire (nécessite stockage des tokens)
    # Pour l'instant, simple message.
    return {"message": f"Déconnexion forcée demandée pour l'utilisateur {user_id}"}

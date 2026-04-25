from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix='/api/auth', tags=['Authentification'])

@router.post('/register', response_model=schemas.Utilisateur)
def register(
    user: schemas.UtilisateurCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == user.email
    ).first()
    if db_user:
        raise HTTPException(400, 'Email déjà enregistré')
    
    hashed_password = auth.get_password_hash(user.mot_de_passe)
    db_user = models.Utilisateur(
        **user.dict(exclude={'mot_de_passe'}),
        mot_de_passe_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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

@router.get('/me', response_model=schemas.Utilisateur)
def get_current_user_info(
    current_user: models.Utilisateur = Depends(auth.get_current_user)
):
    return current_user

@router.put('/me', response_model=schemas.Utilisateur)
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

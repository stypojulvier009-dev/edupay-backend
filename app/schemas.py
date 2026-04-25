from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN_ECOLE = "admin_ecole"
    DIRECTEUR = "directeur"
    COMPTABLE = "comptable"
    CAISSIER = "caissier"
    ENSEIGNANT = "enseignant"
    PARENT = "parent"

class TypeAbonnementEnum(str, Enum):
    GRATUIT = "gratuit"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    nom: str
    ecole_id: Optional[int] = None

# ══════════════════════════════════════════════════════════════
# ABONNEMENTS (MONÉTISATION)
# ══════════════════════════════════════════════════════════════

class AbonnementBase(BaseModel):
    nom: str
    type: TypeAbonnementEnum
    prix_mensuel: float
    prix_annuel: float
    max_ecoles: int
    max_eleves: int
    max_utilisateurs: int
    support_prioritaire: bool = False
    api_access: bool = False
    rapports_avances: bool = False
    sms_inclus: int = 0
    stockage_gb: int = 1

class AbonnementOut(AbonnementBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class SouscriptionCreate(BaseModel):
    ecole_id: int
    abonnement_id: int
    duree_mois: int = 1
    methode_paiement: str

class SouscriptionOut(BaseModel):
    id: int
    ecole_id: int
    abonnement_id: int
    date_debut: datetime
    date_fin: datetime
    actif: bool
    montant_paye: float
    abonnement: Optional[AbonnementOut] = None
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# GÉOLOCALISATION
# ══════════════════════════════════════════════════════════════

class CommuneBase(BaseModel):
    nom: str
    code: Optional[str] = None
    population: Optional[int] = None
    superficie_km2: Optional[float] = None

class CommuneOut(CommuneBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class QuartierBase(BaseModel):
    nom: str
    commune_id: int
    code_postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class QuartierOut(QuartierBase):
    id: int
    commune: Optional[CommuneOut] = None
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# ÉCOLES
# ══════════════════════════════════════════════════════════════

class EcoleCreate(BaseModel):
    nom: str
    code: str
    type: Optional[str] = None
    quartier_id: Optional[int] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    directeur_nom: Optional[str] = None
    directeur_telephone: Optional[str] = None
    capacite_eleves: Optional[int] = None

class EcoleOut(BaseModel):
    id: int
    nom: str
    code: str
    type: Optional[str] = None
    quartier: Optional[QuartierOut] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    actif: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# UTILISATEURS
# ══════════════════════════════════════════════════════════════

class UtilisateurCreate(BaseModel):
    nom: str
    prenom: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    password: str
    role: RoleEnum = RoleEnum.CAISSIER
    ecole_id: Optional[int] = None

class UtilisateurOut(BaseModel):
    id: int
    nom: str
    prenom: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    role: RoleEnum
    ecole_id: Optional[int] = None
    actif: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# CLASSES
# ══════════════════════════════════════════════════════════════

class ClasseCreate(BaseModel):
    nom: str
    niveau: Optional[str] = None
    ecole_id: int
    annee_scolaire: str
    capacite: int = 50
    titulaire_nom: Optional[str] = None

class ClasseOut(ClasseCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# PARENTS
# ══════════════════════════════════════════════════════════════

class ParentCreate(BaseModel):
    nom: str
    prenom: Optional[str] = None
    telephone: str
    email: Optional[str] = None
    adresse: Optional[str] = None
    profession: Optional[str] = None
    lien_parente: Optional[str] = None

class ParentOut(ParentCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# ÉTUDIANTS
# ══════════════════════════════════════════════════════════════

class EtudiantCreate(BaseModel):
    nom: str
    prenom: str
    matricule: str
    date_naissance: Optional[datetime] = None
    sexe: Optional[str] = None
    ecole_id: int
    classe_id: Optional[int] = None
    parent_id: Optional[int] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    boursier: bool = False
    pourcentage_bourse: float = 0.0

class EtudiantOut(BaseModel):
    id: int
    nom: str
    prenom: str
    matricule: str
    date_naissance: Optional[datetime] = None
    sexe: Optional[str] = None
    ecole_id: int
    classe: Optional[ClasseOut] = None
    parent: Optional[ParentOut] = None
    boursier: bool
    pourcentage_bourse: float
    actif: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# FRAIS SCOLAIRES
# ══════════════════════════════════════════════════════════════

class FraisScolaireCreate(BaseModel):
    ecole_id: int
    nom: str
    montant: float
    devise: str = "USD"
    annee_scolaire: str
    obligatoire: bool = True
    description: Optional[str] = None

class FraisScolaireOut(FraisScolaireCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# ÉCHÉANCIERS
# ══════════════════════════════════════════════════════════════

class EcheancierCreate(BaseModel):
    etudiant_id: int
    montant_total: float
    nombre_tranches: int = 3
    date_fin: datetime

class TrancheOut(BaseModel):
    id: int
    numero: int
    montant: float
    date_echeance: datetime
    date_paiement: Optional[datetime] = None
    payee: bool
    class Config:
        from_attributes = True

class EcheancierOut(BaseModel):
    id: int
    etudiant_id: int
    montant_total: float
    montant_paye: float
    montant_restant: float
    nombre_tranches: int
    statut: str
    tranches: List[TrancheOut] = []
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# PAIEMENTS
# ══════════════════════════════════════════════════════════════

class PaiementCreate(BaseModel):
    etudiant_id: int
    montant: float
    devise: str = "USD"
    type_frais: str
    statut: str = "paye"
    methode_paiement: Optional[str] = None
    notes: Optional[str] = None

class PaiementOut(BaseModel):
    id: int
    etudiant_id: int
    montant: float
    devise: str
    type_frais: str
    statut: str
    methode_paiement: Optional[str] = None
    reference: str
    date: datetime
    etudiant: Optional[EtudiantOut] = None
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════════════════════

class NotificationCreate(BaseModel):
    ecole_id: int
    type: str  # SMS, Email
    destinataire: str
    sujet: Optional[str] = None
    message: str

class NotificationOut(NotificationCreate):
    id: int
    statut: str
    cout: float
    date_envoi: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

# ══════════════════════════════════════════════════════════════
# STATISTIQUES AVANCÉES
# ══════════════════════════════════════════════════════════════

class DashboardStats(BaseModel):
    total_etudiants: int
    total_paiements: int
    total_encaisse: float
    taux_paiement: float
    etudiants_actifs: int
    etudiants_boursiers: int
    paiements_en_attente: int
    montant_en_attente: float

class StatsEcole(BaseModel):
    ecole_id: int
    nom_ecole: str
    total_etudiants: int
    total_encaisse: float
    taux_occupation: float
    revenus_mensuels: List[dict]
    top_classes: List[dict]

class RapportFinancier(BaseModel):
    periode_debut: datetime
    periode_fin: datetime
    total_revenus: float
    total_depenses: float
    benefice_net: float
    paiements_par_methode: dict
    evolution_mensuelle: List[dict]

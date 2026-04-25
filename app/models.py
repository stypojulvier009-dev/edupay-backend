from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN_ECOLE = "admin_ecole"
    DIRECTEUR = "directeur"
    COMPTABLE = "comptable"
    CAISSIER = "caissier"
    ENSEIGNANT = "enseignant"
    PARENT = "parent"

class StatutPaiementEnum(str, enum.Enum):
    PAYE = "paye"
    PARTIEL = "partiel"
    EN_ATTENTE = "en_attente"
    ANNULE = "annule"
    REMBOURSE = "rembourse"

class TypeAbonnementEnum(str, enum.Enum):
    GRATUIT = "gratuit"
    BASIC = "basic"           # 50$/mois - 1 école, 500 élèves
    PRO = "pro"               # 150$/mois - 3 écoles, 2000 élèves
    ENTERPRISE = "enterprise" # 500$/mois - illimité + support prioritaire
    CUSTOM = "custom"         # Prix sur mesure

# ══════════════════════════════════════════════════════════════
# SYSTÈME D'ABONNEMENT (MONÉTISATION PRINCIPALE)
# ══════════════════════════════════════════════════════════════

class Abonnement(Base):
    __tablename__ = "abonnements"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    type = Column(SQLEnum(TypeAbonnementEnum), default=TypeAbonnementEnum.GRATUIT)
    prix_mensuel = Column(Float, default=0.0)
    prix_annuel = Column(Float, default=0.0)  # Réduction 20% si annuel
    max_ecoles = Column(Integer, default=1)
    max_eleves = Column(Integer, default=100)
    max_utilisateurs = Column(Integer, default=5)
    support_prioritaire = Column(Boolean, default=False)
    api_access = Column(Boolean, default=False)
    rapports_avances = Column(Boolean, default=False)
    sms_inclus = Column(Integer, default=0)  # SMS gratuits par mois
    stockage_gb = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    souscriptions = relationship("Souscription", back_populates="abonnement")

class Souscription(Base):
    __tablename__ = "souscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    abonnement_id = Column(Integer, ForeignKey("abonnements.id"), nullable=False)
    date_debut = Column(DateTime, default=datetime.utcnow)
    date_fin = Column(DateTime, nullable=False)
    actif = Column(Boolean, default=True)
    auto_renouvellement = Column(Boolean, default=True)
    montant_paye = Column(Float, nullable=False)
    methode_paiement = Column(String)  # Mobile Money, Carte, Virement
    transaction_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="souscriptions")
    abonnement = relationship("Abonnement", back_populates="souscriptions")

# ══════════════════════════════════════════════════════════════
# GÉOLOCALISATION LUBUMBASHI (VALEUR AJOUTÉE)
# ══════════════════════════════════════════════════════════════

class Commune(Base):
    __tablename__ = "communes"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True)
    population = Column(Integer)
    superficie_km2 = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quartiers = relationship("Quartier", back_populates="commune")

class Quartier(Base):
    __tablename__ = "quartiers"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    commune_id = Column(Integer, ForeignKey("communes.id"), nullable=False)
    code_postal = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    commune = relationship("Commune", back_populates="quartiers")
    ecoles = relationship("Ecole", back_populates="quartier")

# ══════════════════════════════════════════════════════════════
# GESTION MULTI-ÉCOLES (SCALABILITÉ)
# ══════════════════════════════════════════════════════════════

class Ecole(Base):
    __tablename__ = "ecoles"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    type = Column(String)  # Primaire, Secondaire, Technique, Université
    quartier_id = Column(Integer, ForeignKey("quartiers.id"))
    adresse = Column(Text)
    telephone = Column(String)
    email = Column(String)
    site_web = Column(String)
    logo_url = Column(String)
    directeur_nom = Column(String)
    directeur_telephone = Column(String)
    capacite_eleves = Column(Integer)
    annee_creation = Column(Integer)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quartier = relationship("Quartier", back_populates="ecoles")
    utilisateurs = relationship("Utilisateur", back_populates="ecole")
    etudiants = relationship("Etudiant", back_populates="ecole")
    classes = relationship("Classe", back_populates="ecole")
    frais_scolaires = relationship("FraisScolaire", back_populates="ecole")
    souscriptions = relationship("Souscription", back_populates="ecole")
    notifications = relationship("Notification", back_populates="ecole")

# ══════════════════════════════════════════════════════════════
# UTILISATEURS AVEC RÔLES AVANCÉS
# ══════════════════════════════════════════════════════════════

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    telephone = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.CAISSIER)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"))
    photo_url = Column(String)
    actif = Column(Boolean, default=True)
    derniere_connexion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="utilisateurs")
    logs = relationship("AuditLog", back_populates="utilisateur")

# ══════════════════════════════════════════════════════════════
# GESTION DES CLASSES
# ══════════════════════════════════════════════════════════════

class Classe(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)  # 6ème A, 1ère Scientifique
    niveau = Column(String)  # Primaire, Secondaire
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    annee_scolaire = Column(String)  # 2024-2025
    capacite = Column(Integer, default=50)
    titulaire_nom = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="classes")
    etudiants = relationship("Etudiant", back_populates="classe")

# ══════════════════════════════════════════════════════════════
# PARENTS/TUTEURS (COMMUNICATION)
# ══════════════════════════════════════════════════════════════

class Parent(Base):
    __tablename__ = "parents"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String)
    telephone = Column(String, nullable=False, index=True)
    email = Column(String)
    adresse = Column(Text)
    profession = Column(String)
    lien_parente = Column(String)  # Père, Mère, Tuteur
    created_at = Column(DateTime, default=datetime.utcnow)
    
    etudiants = relationship("Etudiant", back_populates="parent")

# ══════════════════════════════════════════════════════════════
# ÉTUDIANTS ENRICHIS
# ══════════════════════════════════════════════════════════════

class Etudiant(Base):
    __tablename__ = "etudiants"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    matricule = Column(String, unique=True, index=True, nullable=False)
    date_naissance = Column(DateTime)
    lieu_naissance = Column(String)
    sexe = Column(String)
    photo_url = Column(String)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"))
    parent_id = Column(Integer, ForeignKey("parents.id"))
    telephone = Column(String)
    adresse = Column(Text)
    groupe_sanguin = Column(String)
    allergies = Column(Text)
    boursier = Column(Boolean, default=False)
    pourcentage_bourse = Column(Float, default=0.0)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="etudiants")
    classe = relationship("Classe", back_populates="etudiants")
    parent = relationship("Parent", back_populates="etudiants")
    paiements = relationship("Paiement", back_populates="etudiant")
    echeanciers = relationship("Echeancier", back_populates="etudiant")

# ══════════════════════════════════════════════════════════════
# FRAIS SCOLAIRES PAR ÉCOLE (FLEXIBILITÉ)
# ══════════════════════════════════════════════════════════════

class FraisScolaire(Base):
    __tablename__ = "frais_scolaires"
    
    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    nom = Column(String, nullable=False)  # Scolarité, Inscription, Examen
    montant = Column(Float, nullable=False)
    devise = Column(String, default="USD")
    annee_scolaire = Column(String)
    obligatoire = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="frais_scolaires")

# ══════════════════════════════════════════════════════════════
# ÉCHÉANCIERS (PAIEMENTS PARTIELS)
# ══════════════════════════════════════════════════════════════

class Echeancier(Base):
    __tablename__ = "echeanciers"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    montant_total = Column(Float, nullable=False)
    montant_paye = Column(Float, default=0.0)
    montant_restant = Column(Float, nullable=False)
    nombre_tranches = Column(Integer, default=3)
    date_debut = Column(DateTime, default=datetime.utcnow)
    date_fin = Column(DateTime)
    statut = Column(String, default="en_cours")  # en_cours, termine, en_retard
    created_at = Column(DateTime, default=datetime.utcnow)
    
    etudiant = relationship("Etudiant", back_populates="echeanciers")
    tranches = relationship("Tranche", back_populates="echeancier")

class Tranche(Base):
    __tablename__ = "tranches"
    
    id = Column(Integer, primary_key=True, index=True)
    echeancier_id = Column(Integer, ForeignKey("echeanciers.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    montant = Column(Float, nullable=False)
    date_echeance = Column(DateTime, nullable=False)
    date_paiement = Column(DateTime)
    payee = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    echeancier = relationship("Echeancier", back_populates="tranches")

# ══════════════════════════════════════════════════════════════
# PAIEMENTS ENRICHIS
# ══════════════════════════════════════════════════════════════

class Paiement(Base):
    __tablename__ = "paiements"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    montant = Column(Float, nullable=False)
    devise = Column(String, default="USD")
    type_frais = Column(String, nullable=False)
    statut = Column(SQLEnum(StatutPaiementEnum), default=StatutPaiementEnum.PAYE)
    methode_paiement = Column(String)  # Espèces, Mobile Money, Carte, Virement
    reference = Column(String, unique=True, index=True)
    numero_transaction = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    caissier_id = Column(Integer, ForeignKey("utilisateurs.id"))
    notes = Column(Text)
    recu_url = Column(String)  # PDF du reçu
    created_at = Column(DateTime, default=datetime.utcnow)
    
    etudiant = relationship("Etudiant", back_populates="paiements")

# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS SMS/EMAIL (MONÉTISATION)
# ══════════════════════════════════════════════════════════════

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    type = Column(String)  # SMS, Email, Push
    destinataire = Column(String, nullable=False)  # Téléphone ou email
    sujet = Column(String)
    message = Column(Text, nullable=False)
    statut = Column(String, default="en_attente")  # en_attente, envoye, echec
    cout = Column(Float, default=0.0)  # Coût par SMS
    date_envoi = Column(DateTime)
    erreur = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ecole = relationship("Ecole", back_populates="notifications")

# ══════════════════════════════════════════════════════════════
# AUDIT TRAIL (SÉCURITÉ & CONFORMITÉ)
# ══════════════════════════════════════════════════════════════

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE, LOGIN
    table_name = Column(String)
    record_id = Column(Integer)
    ancien_valeur = Column(Text)  # JSON
    nouvelle_valeur = Column(Text)  # JSON
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    utilisateur = relationship("Utilisateur", back_populates="logs")

# ══════════════════════════════════════════════════════════════
# RAPPORTS PERSONNALISÉS (VALEUR AJOUTÉE PRO)
# ══════════════════════════════════════════════════════════════

class Rapport(Base):
    __tablename__ = "rapports"
    
    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    titre = Column(String, nullable=False)
    type = Column(String)  # Financier, Statistique, Personnalisé
    periode_debut = Column(DateTime)
    periode_fin = Column(DateTime)
    fichier_url = Column(String)  # PDF/Excel généré
    genere_par = Column(Integer, ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# INTÉGRATIONS TIERCES (API MARKETPLACE)
# ══════════════════════════════════════════════════════════════

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)  # Mobile Money, Comptabilité, SMS Gateway
    type = Column(String)
    api_key = Column(String)
    api_secret = Column(String)
    webhook_url = Column(String)
    actif = Column(Boolean, default=False)
    config = Column(Text)  # JSON configuration
    created_at = Column(DateTime, default=datetime.utcnow)

# -*- coding: utf-8 -*-
"""
MODELES SUPPLEMENTAIRES POUR GESTION COMPLETE ECOLE
Presences, Journaux, Cours, Examens, Utilisateurs en attente
"""

modeles_supplementaires = '''
# AJOUTER CES MODELES DANS models.py

# ══════════════════════════════════════════════════════════════
# GESTION DES UTILISATEURS (ADMIN)
# ══════════════════════════════════════════════════════════════

class DemandeInscription(Base):
    __tablename__ = "demandes_inscription"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telephone = Column(String)
    role_demande = Column(SQLEnum(RoleEnum), nullable=False)
    mot_de_passe_hash = Column(String, nullable=False)
    
    # Justificatifs
    cv_url = Column(String)
    diplome_url = Column(String)
    photo_url = Column(String)
    lettre_motivation = Column(Text)
    
    # Statut
    statut = Column(String, default="en_attente")  # en_attente, approuve, rejete
    date_demande = Column(DateTime, default=datetime.utcnow)
    date_traitement = Column(DateTime)
    traite_par = Column(Integer, ForeignKey("utilisateurs.id"))
    motif_rejet = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# PRESENCES ET ABSENCES
# ══════════════════════════════════════════════════════════════

class Presence(Base):
    __tablename__ = "presences"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Statut
    present = Column(Boolean, default=True)
    retard = Column(Boolean, default=False)
    justifie = Column(Boolean, default=False)
    
    # Details
    heure_arrivee = Column(String)
    motif_absence = Column(Text)
    justificatif_url = Column(String)
    
    # Enregistrement
    enregistre_par = Column(Integer, ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    etudiant = relationship("Etudiant", back_populates="presences")
    classe = relationship("Classe", back_populates="presences")

class RapportAbsence(Base):
    __tablename__ = "rapports_absences"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    periode_debut = Column(DateTime, nullable=False)
    periode_fin = Column(DateTime, nullable=False)
    
    # Statistiques
    total_jours = Column(Integer, default=0)
    jours_presents = Column(Integer, default=0)
    jours_absents = Column(Integer, default=0)
    jours_retard = Column(Integer, default=0)
    taux_presence = Column(Float, default=0.0)  # Pourcentage
    
    # Alertes
    alerte_envoyee = Column(Boolean, default=False)
    parent_notifie = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# JOURNAL DE CLASSE
# ══════════════════════════════════════════════════════════════

class JournalClasse(Base):
    __tablename__ = "journaux_classe"
    
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Contenu
    titre = Column(String, nullable=False)
    contenu = Column(Text, nullable=False)
    type = Column(String)  # cours, activite, evenement, remarque
    
    # Matiere
    matiere = Column(String)
    professeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    
    # Fichiers
    fichiers_urls = Column(Text)  # JSON array
    
    # Visibilite
    visible_parents = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    classe = relationship("Classe", back_populates="journaux")

# ══════════════════════════════════════════════════════════════
# COURS ET EMPLOI DU TEMPS
# ══════════════════════════════════════════════════════════════

class Matiere(Base):
    __tablename__ = "matieres"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    code = Column(String, unique=True)
    description = Column(Text)
    coefficient = Column(Float, default=1.0)
    couleur_hex = Column(String)
    
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Professeur(Base):
    __tablename__ = "professeurs"
    
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    
    # Informations
    specialite = Column(String)
    diplome = Column(String)
    experience_annees = Column(Integer)
    
    # Disponibilite
    disponible = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Cours(Base):
    __tablename__ = "cours"
    
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    professeur_id = Column(Integer, ForeignKey("professeurs.id"), nullable=False)
    
    # Horaire
    jour_semaine = Column(String, nullable=False)  # Lundi, Mardi, etc.
    heure_debut = Column(String, nullable=False)  # 08:00
    heure_fin = Column(String, nullable=False)    # 10:00
    salle = Column(String)
    
    # Statut
    actif = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    classe = relationship("Classe", back_populates="cours")
    matiere = relationship("Matiere")
    professeur = relationship("Professeur")

class SeanceCours(Base):
    __tablename__ = "seances_cours"
    
    id = Column(Integer, primary_key=True, index=True)
    cours_id = Column(Integer, ForeignKey("cours.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Contenu
    titre = Column(String, nullable=False)
    objectifs = Column(Text)
    contenu = Column(Text)
    devoirs = Column(Text)
    
    # Statut
    effectue = Column(Boolean, default=False)
    annule = Column(Boolean, default=False)
    motif_annulation = Column(Text)
    
    # Fichiers
    supports_urls = Column(Text)  # JSON array
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# EXAMENS ET EVALUATIONS
# ══════════════════════════════════════════════════════════════

class TypeExamen(str, enum.Enum):
    INTERROGATION = "interrogation"
    DEVOIR = "devoir"
    COMPOSITION = "composition"
    EXAMEN_BLANC = "examen_blanc"
    EXAMEN_FINAL = "examen_final"

class Examen(Base):
    __tablename__ = "examens"
    
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    professeur_id = Column(Integer, ForeignKey("professeurs.id"), nullable=False)
    
    # Informations
    titre = Column(String, nullable=False)
    type = Column(SQLEnum(TypeExamen), nullable=False)
    description = Column(Text)
    
    # Date et heure
    date_examen = Column(DateTime, nullable=False)
    duree_minutes = Column(Integer, nullable=False)
    salle = Column(String)
    
    # Notation
    note_max = Column(Float, default=20.0)
    coefficient = Column(Float, default=1.0)
    
    # Statut
    publie = Column(Boolean, default=False)
    termine = Column(Boolean, default=False)
    
    # Fichiers
    sujet_url = Column(String)
    corrige_url = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    classe = relationship("Classe", back_populates="examens")
    matiere = relationship("Matiere")
    professeur = relationship("Professeur")
    notes = relationship("Note", back_populates="examen")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    examen_id = Column(Integer, ForeignKey("examens.id"), nullable=False)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    
    # Note
    note = Column(Float, nullable=False)
    note_max = Column(Float, default=20.0)
    appreciation = Column(Text)
    
    # Statut
    absent = Column(Boolean, default=False)
    copie_url = Column(String)
    
    # Enregistrement
    enregistre_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_enregistrement = Column(DateTime, default=datetime.utcnow)
    
    examen = relationship("Examen", back_populates="notes")
    etudiant = relationship("Etudiant", back_populates="notes")

class Bulletin(Base):
    __tablename__ = "bulletins"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # Periode
    trimestre = Column(Integer, nullable=False)  # 1, 2, 3
    annee_scolaire = Column(String, nullable=False)
    
    # Moyennes
    moyenne_generale = Column(Float)
    rang = Column(Integer)
    total_eleves = Column(Integer)
    
    # Appreciation
    appreciation_generale = Column(Text)
    decision = Column(String)  # Admis, Redouble, etc.
    
    # Fichier
    bulletin_url = Column(String)
    
    # Statut
    publie = Column(Boolean, default=False)
    date_publication = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# ELIGIBILITE AUX EXAMENS
# ══════════════════════════════════════════════════════════════

class EligibiliteExamen(Base):
    __tablename__ = "eligibilites_examen"
    
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    examen_id = Column(Integer, ForeignKey("examens.id"), nullable=False)
    
    # Eligibilite
    eligible = Column(Boolean, default=True)
    motif_ineligibilite = Column(Text)
    
    # Criteres
    paiement_a_jour = Column(Boolean, default=False)
    presence_suffisante = Column(Boolean, default=True)
    documents_complets = Column(Boolean, default=True)
    
    # Verification
    verifie_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_verification = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# CAHIER DE PAIEMENTS (REGISTRE)
# ══════════════════════════════════════════════════════════════

class RegistrePaiement(Base):
    __tablename__ = "registre_paiements"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    
    # Totaux journaliers
    total_especes = Column(Float, default=0.0)
    total_mobile_money = Column(Float, default=0.0)
    total_banque = Column(Float, default=0.0)
    total_agence = Column(Float, default=0.0)
    total_general = Column(Float, default=0.0)
    
    # Nombre de transactions
    nombre_transactions = Column(Integer, default=0)
    
    # Verification
    verifie = Column(Boolean, default=False)
    verifie_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_verification = Column(DateTime)
    
    # Cloture
    cloture = Column(Boolean, default=False)
    cloture_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_cloture = Column(DateTime)
    
    # Observations
    observations = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# RELATIONS A AJOUTER AUX MODELES EXISTANTS
# ══════════════════════════════════════════════════════════════

# Dans Etudiant:
    presences = relationship("Presence", back_populates="etudiant")
    notes = relationship("Note", back_populates="etudiant")

# Dans Classe:
    presences = relationship("Presence", back_populates="classe")
    journaux = relationship("JournalClasse", back_populates="classe")
    cours = relationship("Cours", back_populates="classe")
    examens = relationship("Examen", back_populates="classe")

# Dans Ecole:
    paiements = relationship("Paiement", back_populates="ecole")
'''

print("Modeles supplementaires crees!")
print("\nFonctionnalites ajoutees:")
print("- Demandes d'inscription (approbation admin)")
print("- Presences et absences")
print("- Rapports d'absences")
print("- Journal de classe")
print("- Matieres et professeurs")
print("- Cours et emploi du temps")
print("- Seances de cours")
print("- Examens et evaluations")
print("- Notes et bulletins")
print("- Eligibilite aux examens")
print("- Registre de paiements (cahier)")

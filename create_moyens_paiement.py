# -*- coding: utf-8 -*-
"""
TOUS LES MOYENS DE PAIEMENT EN RDC
Pour Complexe Scolaire Oasis des Juniors
"""

moyens_paiement_rdc = '''
# AJOUTER CES ENUMS ET MODELES DANS models.py

# ══════════════════════════════════════════════════════════════
# MOYENS DE PAIEMENT RDC
# ══════════════════════════════════════════════════════════════

class ModePaiementEnum(str, enum.Enum):
    # Mobile Money
    MPESA = "mpesa"                    # Vodacom M-Pesa
    AIRTEL_MONEY = "airtel_money"      # Airtel Money
    ORANGE_MONEY = "orange_money"      # Orange Money
    AFRIMONEY = "afrimoney"            # Africell AfriMoney
    
    # Agences de transfert
    WESTERN_UNION = "western_union"    # Western Union
    MONEYGRAM = "moneygram"            # MoneyGram
    RIA = "ria"                        # Ria Money Transfer
    WORLDREMIT = "worldremit"          # WorldRemit
    
    # Banques RDC
    RAWBANK = "rawbank"                # Rawbank
    EQUITY_BANK = "equity_bank"        # Equity Bank
    TRUST_MERCHANT_BANK = "tmb"        # Trust Merchant Bank
    SOFIBANQUE = "sofibanque"          # Sofibanque
    ECOBANK = "ecobank"                # Ecobank
    BGFI = "bgfi"                      # BGFI Bank
    
    # Autres
    ESPECES = "especes"                # Cash
    CHEQUE = "cheque"                  # Cheque bancaire
    VIREMENT = "virement"              # Virement bancaire
    CARTE_BANCAIRE = "carte_bancaire"  # Visa/Mastercard

class StatutPaiementEnum(str, enum.Enum):
    EN_ATTENTE = "en_attente"          # En attente de confirmation
    EN_COURS = "en_cours"              # Transaction en cours
    VALIDE = "valide"                  # Paiement valide
    REJETE = "rejete"                  # Paiement rejete
    ANNULE = "annule"                  # Paiement annule
    REMBOURSE = "rembourse"            # Paiement rembourse

# ══════════════════════════════════════════════════════════════
# MODELE PAIEMENT COMPLET
# ══════════════════════════════════════════════════════════════

class Paiement(Base):
    __tablename__ = "paiements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations etudiant
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    
    # Montant
    montant = Column(Float, nullable=False)
    devise = Column(String, default="CDF")  # CDF ou USD
    taux_change = Column(Float)  # Si conversion USD -> CDF
    
    # Type de frais
    type_frais = Column(String, nullable=False)  # Inscription, Minerval, etc.
    description = Column(Text)
    
    # Mode de paiement
    mode_paiement = Column(SQLEnum(ModePaiementEnum), nullable=False)
    statut = Column(SQLEnum(StatutPaiementEnum), default=StatutPaiementEnum.EN_ATTENTE)
    
    # References
    reference = Column(String, unique=True, index=True, nullable=False)  # REF-OASIS-XXXXX
    numero_transaction = Column(String)  # ID de l'operateur/banque
    numero_recu = Column(String, unique=True)  # Numero du recu imprime
    
    # Details selon le mode de paiement
    # Pour Mobile Money
    numero_telephone = Column(String)  # +243XXXXXXXXX
    nom_expediteur = Column(String)    # Nom du payeur
    
    # Pour Agences (Western Union, MoneyGram, etc.)
    code_mtcn = Column(String)         # Code de transfert
    agence_nom = Column(String)        # Nom de l'agence
    agence_adresse = Column(String)    # Adresse de l'agence
    
    # Pour Banques
    numero_compte = Column(String)     # Numero de compte
    nom_banque = Column(String)        # Nom de la banque
    numero_cheque = Column(String)     # Si paiement par cheque
    
    # Pour Especes
    numero_bordereau = Column(String)  # Bordereau de caisse
    
    # Frais et commissions
    frais_transaction = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    montant_net = Column(Float)  # Montant recu par l'ecole
    
    # Dates
    date_paiement = Column(DateTime, default=datetime.utcnow)
    date_validation = Column(DateTime)
    date_comptabilisation = Column(DateTime)
    
    # Utilisateurs
    enregistre_par = Column(Integer, ForeignKey("utilisateurs.id"))  # Caissier
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"))      # Comptable
    
    # Documents
    recu_url = Column(String)          # PDF du recu
    preuve_paiement_url = Column(String)  # Photo/scan de la preuve
    
    # Notes
    notes = Column(Text)
    notes_internes = Column(Text)      # Visibles uniquement par admin
    
    # Metadata
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="paiements")
    ecole = relationship("Ecole", back_populates="paiements")

# ══════════════════════════════════════════════════════════════
# CONFIGURATION DES MOYENS DE PAIEMENT
# ══════════════════════════════════════════════════════════════

class ConfigurationPaiement(Base):
    __tablename__ = "configurations_paiement"
    
    id = Column(Integer, primary_key=True, index=True)
    mode_paiement = Column(SQLEnum(ModePaiementEnum), unique=True, nullable=False)
    
    # Activation
    actif = Column(Boolean, default=True)
    visible = Column(Boolean, default=True)  # Afficher dans l'app
    
    # Informations affichage
    nom_affichage = Column(String, nullable=False)
    description = Column(Text)
    logo_url = Column(String)
    couleur_hex = Column(String)
    icone = Column(String)
    ordre_affichage = Column(Integer, default=0)
    
    # Frais et limites
    frais_pourcentage = Column(Float, default=0.0)
    frais_fixe = Column(Float, default=0.0)
    montant_min = Column(Float, default=0.0)
    montant_max = Column(Float)
    
    # Configuration technique (pour Mobile Money, API, etc.)
    api_key = Column(String)
    api_secret = Column(String)
    merchant_id = Column(String)
    api_base_url = Column(String)
    callback_url = Column(String)
    mode_test = Column(Boolean, default=True)
    
    # Instructions pour l'utilisateur
    instructions = Column(Text)  # Comment payer avec ce moyen
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# HISTORIQUE DES TRANSACTIONS PAR OPERATEUR
# ══════════════════════════════════════════════════════════════

class TransactionOperateur(Base):
    __tablename__ = "transactions_operateur"
    
    id = Column(Integer, primary_key=True, index=True)
    paiement_id = Column(Integer, ForeignKey("paiements.id"), nullable=False)
    
    # Operateur
    operateur = Column(SQLEnum(ModePaiementEnum), nullable=False)
    
    # Transaction
    transaction_id = Column(String, unique=True, index=True)
    reference_externe = Column(String)  # Reference de l'operateur
    statut = Column(String, default="en_attente")
    
    # Montants
    montant_demande = Column(Float, nullable=False)
    montant_recu = Column(Float)
    frais = Column(Float, default=0.0)
    
    # Dates
    date_initiation = Column(DateTime, default=datetime.utcnow)
    date_completion = Column(DateTime)
    date_expiration = Column(DateTime)
    
    # Reponses API
    requete_api = Column(Text)  # JSON de la requete
    reponse_api = Column(Text)  # JSON de la reponse
    webhook_data = Column(Text)  # Donnees du callback
    
    # Erreurs
    code_erreur = Column(String)
    message_erreur = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    paiement = relationship("Paiement", back_populates="transaction_operateur")

# ══════════════════════════════════════════════════════════════
# RAPPROCHEMENT BANCAIRE
# ══════════════════════════════════════════════════════════════

class RapprochementBancaire(Base):
    __tablename__ = "rapprochements_bancaires"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Periode
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=False)
    
    # Operateur/Banque
    operateur = Column(SQLEnum(ModePaiementEnum), nullable=False)
    
    # Soldes
    solde_initial = Column(Float, default=0.0)
    total_entrees = Column(Float, default=0.0)
    total_sorties = Column(Float, default=0.0)
    total_frais = Column(Float, default=0.0)
    solde_final_calcule = Column(Float, default=0.0)
    solde_final_reel = Column(Float)  # Du releve bancaire
    
    # Ecart
    ecart = Column(Float, default=0.0)
    ecart_justifie = Column(Boolean, default=False)
    justification = Column(Text)
    
    # Statistiques
    nombre_transactions = Column(Integer, default=0)
    nombre_reussies = Column(Integer, default=0)
    nombre_echouees = Column(Integer, default=0)
    
    # Validation
    valide = Column(Boolean, default=False)
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"))
    date_validation = Column(DateTime)
    
    # Documents
    releve_bancaire_url = Column(String)
    rapport_url = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
'''

print("Modeles de paiement RDC crees!")
print("\nMoyens de paiement supportes:")
print("\nMOBILE MONEY:")
print("- Vodacom M-Pesa")
print("- Airtel Money")
print("- Orange Money")
print("- Africell AfriMoney")
print("\nAGENCES DE TRANSFERT:")
print("- Western Union")
print("- MoneyGram")
print("- Ria Money Transfer")
print("- WorldRemit")
print("\nBANQUES:")
print("- Rawbank")
print("- Equity Bank")
print("- Trust Merchant Bank (TMB)")
print("- Sofibanque")
print("- Ecobank")
print("- BGFI Bank")
print("\nAUTRES:")
print("- Especes (Cash)")
print("- Cheque bancaire")
print("- Virement bancaire")
print("- Carte bancaire (Visa/Mastercard)")

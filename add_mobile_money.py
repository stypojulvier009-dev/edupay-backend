# -*- coding: utf-8 -*-
"""
Ajout des moyens de paiement Mobile Money RDC
et adaptation pour Complexe Scolaire Oasis des Juniors
"""

mobile_money_models = '''
# Ajouter ces modeles dans models.py

class OperateurMobileMoneyEnum(str, enum.Enum):
    MPESA = "mpesa"              # Vodacom M-Pesa
    AIRTEL_MONEY = "airtel_money" # Airtel Money
    ORANGE_MONEY = "orange_money" # Orange Money
    AFRIMONEY = "afrimoney"       # Africell AfriMoney

class StatutTransactionEnum(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    REUSSIE = "reussie"
    ECHOUEE = "echouee"
    ANNULEE = "annulee"
    REMBOURSEE = "remboursee"

# ══════════════════════════════════════════════════════════════
# MOBILE MONEY RDC (VODACOM, AIRTEL, ORANGE, AFRICELL)
# ══════════════════════════════════════════════════════════════

class TransactionMobileMoney(Base):
    __tablename__ = "transactions_mobile_money"
    
    id = Column(Integer, primary_key=True, index=True)
    paiement_id = Column(Integer, ForeignKey("paiements.id"), nullable=False)
    operateur = Column(SQLEnum(OperateurMobileMoneyEnum), nullable=False)
    numero_telephone = Column(String, nullable=False)  # +243XXXXXXXXX
    montant = Column(Float, nullable=False)
    devise = Column(String, default="CDF")  # CDF ou USD
    
    # Informations transaction
    transaction_id = Column(String, unique=True, index=True)  # ID operateur
    reference_externe = Column(String)  # Reference M-Pesa/Airtel
    statut = Column(SQLEnum(StatutTransactionEnum), default=StatutTransactionEnum.EN_ATTENTE)
    
    # Frais et commissions
    frais_operateur = Column(Float, default=0.0)  # Frais M-Pesa/Airtel
    commission_edupay = Column(Float, default=0.0)  # Notre commission (2-5%)
    montant_net = Column(Float)  # Montant recu par l'ecole
    
    # Dates
    date_initiation = Column(DateTime, default=datetime.utcnow)
    date_completion = Column(DateTime)
    date_expiration = Column(DateTime)  # Timeout apres 5 minutes
    
    # Webhook et callbacks
    callback_url = Column(String)
    webhook_reponse = Column(Text)  # JSON de la reponse operateur
    
    # Erreurs
    code_erreur = Column(String)
    message_erreur = Column(Text)
    
    # Metadata
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    paiement = relationship("Paiement", back_populates="transaction_mobile_money")

# ══════════════════════════════════════════════════════════════
# CONFIGURATION OPERATEURS MOBILE MONEY
# ══════════════════════════════════════════════════════════════

class ConfigurationMobileMoney(Base):
    __tablename__ = "configurations_mobile_money"
    
    id = Column(Integer, primary_key=True, index=True)
    operateur = Column(SQLEnum(OperateurMobileMoneyEnum), unique=True, nullable=False)
    
    # Credentials API
    api_key = Column(String)
    api_secret = Column(String)
    merchant_id = Column(String)
    merchant_name = Column(String, default="Complexe Scolaire Oasis des Juniors")
    
    # URLs API
    api_base_url = Column(String)
    callback_url = Column(String)
    webhook_url = Column(String)
    
    # Configuration
    actif = Column(Boolean, default=True)
    mode_test = Column(Boolean, default=True)  # Sandbox ou Production
    timeout_secondes = Column(Integer, default=300)  # 5 minutes
    
    # Frais et limites
    frais_pourcentage = Column(Float, default=2.0)  # 2% de frais
    frais_fixe = Column(Float, default=0.0)
    montant_min = Column(Float, default=100.0)  # 100 CDF minimum
    montant_max = Column(Float, default=5000000.0)  # 5M CDF maximum
    
    # Metadata
    logo_url = Column(String)
    couleur_hex = Column(String)  # Pour l'UI
    ordre_affichage = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# ══════════════════════════════════════════════════════════════
# HISTORIQUE SOLDES MOBILE MONEY (RECONCILIATION)
# ══════════════════════════════════════════════════════════════

class SoldeMobileMoney(Base):
    __tablename__ = "soldes_mobile_money"
    
    id = Column(Integer, primary_key=True, index=True)
    operateur = Column(SQLEnum(OperateurMobileMoneyEnum), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Soldes
    solde_debut = Column(Float, default=0.0)
    total_entrees = Column(Float, default=0.0)  # Paiements recus
    total_sorties = Column(Float, default=0.0)  # Retraits/Remboursements
    total_frais = Column(Float, default=0.0)
    solde_fin = Column(Float, default=0.0)
    
    # Statistiques
    nombre_transactions = Column(Integer, default=0)
    nombre_reussies = Column(Integer, default=0)
    nombre_echouees = Column(Integer, default=0)
    
    # Reconciliation
    reconcilie = Column(Boolean, default=False)
    date_reconciliation = Column(DateTime)
    ecart = Column(Float, default=0.0)  # Difference avec releve operateur
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
'''

# Mettre a jour Paiement pour ajouter la relation
paiement_update = '''
# Dans la classe Paiement, ajouter:
    transaction_mobile_money = relationship("TransactionMobileMoney", back_populates="paiement", uselist=False)
'''

print("Modeles Mobile Money RDC crees!")
print("\nOperateurs supportes:")
print("- Vodacom M-Pesa")
print("- Airtel Money")
print("- Orange Money")
print("- Africell AfriMoney")

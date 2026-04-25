# 🎓 EduPay Backend - API Ultra-Premium

Backend FastAPI pour le système de paiement électronique des frais scolaires EduPay.

## 🚀 Fonctionnalités Niveau Mondial

### 💰 Monétisation
- **4 Plans d'Abonnement**: Gratuit, Basic ($50/mois), Pro ($150/mois), Enterprise ($500/mois)
- **Commissions Mobile Money**: 2-5% sur chaque transaction
- **SMS Premium**: $0.05 par SMS
- **Rapports Premium**: $10-50 par rapport
- **API Marketplace**: Intégrations tierces payantes
- **White Label**: $5000+ pour personnalisation complète

### 🏢 Multi-Tenant
- Gestion illimitée d'écoles
- Isolation complète des données par école
- Tableau de bord personnalisé par école

### 📍 Géolocalisation
- 8 Communes de Lubumbashi intégrées
- 30+ Quartiers mappés
- Recherche géographique avancée

### 👥 Gestion Complète
- **7 Rôles**: super_admin, admin_ecole, directeur, comptable, caissier, enseignant, parent
- **Classes**: Gestion des niveaux scolaires
- **Parents**: Profils complets avec contacts
- **Étudiants**: Dossiers académiques et financiers
- **Frais Scolaires**: Configuration flexible par classe

### 💳 Paiements Avancés
- **Modes**: Espèces, Mobile Money, Carte bancaire, Virement
- **Devises**: USD, CDF, EUR
- **Paiements Partiels**: Tranches personnalisables
- **Bourses**: Réductions automatiques
- **Échéanciers**: Calendriers de paiement flexibles

### 📊 Rapports & Analytics
- Rapports financiers (PDF, Excel, CSV)
- Statistiques en temps réel
- Tableaux de bord interactifs
- Prévisions de revenus

### 🔔 Notifications
- SMS automatiques
- Emails transactionnels
- Notifications in-app
- Rappels de paiement

### 🔒 Sécurité & Conformité
- Authentification JWT
- Audit trail complet
- Logs d'activité
- Conformité RGPD

### 🔌 Intégrations
- Mobile Money (M-Pesa, Airtel Money, Orange Money)
- SMS Gateway (Twilio, Africa's Talking)
- Email (SendGrid, AWS SES)
- Comptabilité (QuickBooks, Sage)

## 📁 Structure du Projet

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── database.py          # Configuration PostgreSQL
│   ├── models.py            # 16 modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   ├── auth.py              # JWT & sécurité
│   ├── init_db.py           # Initialisation DB
│   └── routers/
│       ├── auth.py          # Authentification
│       ├── abonnements.py   # Plans & souscriptions
│       ├── geolocalisation.py # Communes & quartiers
│       ├── ecoles.py        # Gestion écoles
│       ├── classes.py       # Gestion classes
│       ├── parents.py       # Gestion parents
│       ├── etudiants.py     # Gestion étudiants
│       ├── frais.py         # Frais scolaires
│       ├── echeanciers.py   # Calendriers paiement
│       ├── paiements.py     # Transactions
│       ├── notifications.py # Alertes
│       ├── rapports.py      # Analytics
│       └── audit.py         # Logs d'audit
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
├── DEPLOIEMENT_RAILWAY.md
├── PITCH_COMMERCIAL.md
└── STRATEGIE_CROISSANCE.md
```

## 🛠️ Installation Locale

### Prérequis
- Python 3.11+
- PostgreSQL 14+
- Git

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/edupay.git
cd edupay/backend
```

### 2. Créer l'Environnement Virtuel
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la Base de Données
```bash
# Créer la base de données PostgreSQL
createdb edupay

# Copier le fichier d'environnement
copy .env.example .env

# Modifier .env avec vos paramètres
DATABASE_URL=postgresql://user:password@localhost/edupay
SECRET_KEY=votre_cle_secrete_ultra_securisee
```

### 5. Initialiser la Base de Données
```bash
python -m app.init_db
```

Cela créera:
- ✅ 4 plans d'abonnement
- ✅ 8 communes de Lubumbashi
- ✅ 30+ quartiers
- ✅ Compte super admin (admin@edupay.cd / Admin123!)

### 6. Lancer le Serveur
```bash
uvicorn app.main:app --reload
```

L'API sera disponible sur: http://localhost:8000

### 7. Tester l'API
```bash
# Documentation interactive
http://localhost:8000/docs

# Tester avec le script
python test_api.py
```

## 🌐 Déploiement Production

Voir [DEPLOIEMENT_RAILWAY.md](DEPLOIEMENT_RAILWAY.md) pour le guide complet.

### Déploiement Rapide sur Railway

```bash
# 1. Installer Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Créer projet
railway init

# 4. Ajouter PostgreSQL
railway add

# 5. Déployer
railway up
```

## 📚 Documentation API

### Authentification

**Login**
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@edupay.cd&password=Admin123!
```

**Réponse**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nom": "Admin",
    "email": "admin@edupay.cd",
    "role": "super_admin"
  }
}
```

### Utiliser le Token

Tous les endpoints nécessitent le header:
```
Authorization: Bearer <votre_token>
```

### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/abonnements` | Liste des plans |
| POST | `/api/abonnements/souscrire` | Souscrire à un plan |
| GET | `/api/geo/communes` | Communes de Lubumbashi |
| POST | `/api/ecoles` | Créer une école |
| GET | `/api/classes` | Liste des classes |
| POST | `/api/etudiants` | Créer un étudiant |
| POST | `/api/paiements` | Enregistrer un paiement |
| GET | `/api/paiements/stats/dashboard` | Statistiques |
| GET | `/api/rapports/stats/financier` | Rapport financier |

Documentation complète: http://localhost:8000/docs

## 🔐 Sécurité

### Variables d'Environnement Sensibles

**JAMAIS** commiter ces valeurs:
- `SECRET_KEY` - Clé JWT (32+ caractères)
- `DATABASE_URL` - URL de connexion PostgreSQL
- `SMTP_PASSWORD` - Mot de passe email
- `SMS_API_KEY` - Clé API SMS

### Bonnes Pratiques
- ✅ Utiliser HTTPS en production
- ✅ Changer le mot de passe admin par défaut
- ✅ Activer les logs d'audit
- ✅ Limiter les tentatives de connexion
- ✅ Valider toutes les entrées utilisateur

## 📊 Base de Données

### 16 Tables Principales

1. **abonnements** - Plans tarifaires
2. **souscriptions** - Abonnements actifs
3. **communes** - Communes de Lubumbashi
4. **quartiers** - Quartiers par commune
5. **ecoles** - Établissements scolaires
6. **utilisateurs** - Comptes utilisateurs
7. **classes** - Niveaux scolaires
8. **parents** - Profils parents
9. **etudiants** - Dossiers étudiants
10. **frais_scolaires** - Configuration des frais
11. **echeanciers** - Calendriers de paiement
12. **tranches** - Échéances de paiement
13. **paiements** - Transactions
14. **notifications** - Alertes
15. **audit_logs** - Logs d'activité
16. **rapports** - Rapports générés

### Schéma Relationnel

```
ecoles (1) ─── (N) utilisateurs
ecoles (1) ─── (N) classes
ecoles (1) ─── (N) parents
ecoles (1) ─── (N) etudiants
classes (1) ─── (N) etudiants
parents (1) ─── (N) etudiants
etudiants (1) ─── (N) paiements
communes (1) ─── (N) quartiers
communes (1) ─── (N) ecoles
```

## 🧪 Tests

```bash
# Tests unitaires
pytest

# Tests d'intégration
python test_api.py

# Coverage
pytest --cov=app tests/
```

## 📈 Performance

### Optimisations
- Index sur colonnes fréquemment recherchées
- Pagination sur toutes les listes
- Cache Redis pour données statiques
- Compression gzip des réponses
- Connection pooling PostgreSQL

### Métriques Cibles
- Temps de réponse: < 200ms
- Disponibilité: 99.9%
- Throughput: 1000 req/s
- Latence DB: < 50ms

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Propriétaire - Tous droits réservés © 2024 EduPay

## 📞 Support

- **Email**: support@edupay.cd
- **Téléphone**: +243 999 999 999
- **Documentation**: https://docs.edupay.cd
- **Status**: https://status.edupay.cd

## 🎯 Roadmap

### Q1 2024
- ✅ Backend API complet
- ✅ Authentification JWT
- ✅ Multi-tenant
- ✅ Géolocalisation Lubumbashi

### Q2 2024
- 🔄 Application mobile Flutter
- 🔄 Intégrations Mobile Money
- 🔄 SMS Gateway
- 🔄 Rapports PDF

### Q3 2024
- 📅 Dashboard analytics avancé
- 📅 API publique pour partenaires
- 📅 Application web React
- 📅 Expansion autres villes RDC

### Q4 2024
- 📅 IA pour prédictions
- 📅 Blockchain pour traçabilité
- 📅 Expansion Afrique francophone
- 📅 Marketplace d'intégrations

---

**Fait avec ❤️ à Lubumbashi, RDC 🇨🇩**

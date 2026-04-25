# EDUPAY - COMPLEXE SCOLAIRE OASIS DES JUNIORS

Application de gestion des paiements scolaires DEDIEE au Complexe Scolaire Oasis des Juniors, Lubumbashi, RDC.

---

## MOYENS DE PAIEMENT SUPPORTES

### MOBILE MONEY RDC
- **Vodacom M-Pesa** - *150# - Le plus utilise en RDC
- **Airtel Money** - *501# - Rapide et fiable
- **Orange Money** - *144# - Disponible partout
- **Africell AfriMoney** - *555# - Economique

### AGENCES DE TRANSFERT
- **Western Union** - Transferts internationaux
- **MoneyGram** - Envois rapides
- **Ria Money Transfer** - Frais reduits
- **WorldRemit** - Transferts en ligne

### BANQUES RDC
- **Rawbank** - Premiere banque RDC
- **Equity Bank** - Reseau etendu
- **Trust Merchant Bank (TMB)** - Services complets
- **Sofibanque** - Banque locale
- **Ecobank** - Reseau panafricain
- **BGFI Bank** - Services premium

### AUTRES MOYENS
- **Especes (Cash)** - Paiement direct a la caisse
- **Cheque bancaire** - Cheques certifies
- **Virement bancaire** - Transferts compte a compte
- **Carte bancaire** - Visa/Mastercard

---

## FONCTIONNALITES

### GESTION DES PAIEMENTS
- Enregistrement multi-moyens de paiement
- Validation automatique ou manuelle
- Generation de recus PDF
- Notifications SMS aux parents
- Historique complet des transactions
- Rapprochement bancaire

### GESTION DES ETUDIANTS
- Dossiers complets (photo, infos medicales)
- Affectation aux classes
- Lien avec les parents
- Bourses et reductions
- Suivi des paiements

### GESTION DES CLASSES
- 6 classes primaires (1ere a 6eme)
- 6 classes secondaires (7eme a 4eme secondaire)
- Capacite par classe
- Titulaires de classe
- Annee scolaire 2024-2025

### FRAIS SCOLAIRES
- Frais d'inscription: 50,000 CDF
- Minerval (3 trimestres): 150,000 CDF chacun
- Frais d'examen: 30,000 CDF
- Uniforme scolaire: 40,000 CDF
- Fournitures: 25,000 CDF

### UTILISATEURS ET ROLES
- **Super Admin** - Acces total
- **Directeur** - Gestion academique
- **Comptable** - Gestion financiere
- **Caissier** - Enregistrement paiements
- **Enseignant** - Consultation
- **Parent** - Suivi enfants

### RAPPORTS ET STATISTIQUES
- Rapports financiers (PDF, Excel)
- Statistiques par mode de paiement
- Suivi des encaissements
- Rapports par classe
- Rapports par periode

---

## INSTALLATION

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/edupay-oasis.git
cd edupay-oasis/backend
```

### 2. Installer les Dependances
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurer la Base de Donnees
```bash
# Creer la base PostgreSQL
createdb edupay_oasis

# Copier le fichier d'environnement
copy .env.example .env

# Modifier .env
DATABASE_URL=postgresql://user:password@localhost/edupay_oasis
SECRET_KEY=votre_cle_secrete_ultra_securisee
```

### 4. Initialiser Oasis des Juniors
```bash
python -m app.init_oasis
```

Cela cree:
- L'ecole Oasis des Juniors
- 4 comptes utilisateurs
- 12 classes (6 primaire + 6 secondaire)
- 7 types de frais scolaires
- Configuration des 20+ moyens de paiement

### 5. Lancer le Serveur
```bash
uvicorn app.main:app --reload
```

API disponible sur: http://localhost:8000

Documentation: http://localhost:8000/docs

---

## COMPTES PAR DEFAUT

| Role | Email | Mot de passe |
|------|-------|--------------|
| Super Admin | admin@oasisdesjuniors.cd | Admin123! |
| Directeur | directeur@oasisdesjuniors.cd | Directeur123! |
| Comptable | comptable@oasisdesjuniors.cd | Comptable123! |
| Caissier | caissier@oasisdesjuniors.cd | Caissier123! |

**IMPORTANT**: Changez ces mots de passe en production!

---

## UTILISATION

### 1. Se Connecter
```bash
POST /api/auth/login
{
  "username": "caissier@oasisdesjuniors.cd",
  "password": "Caissier123!"
}
```

### 2. Enregistrer un Paiement

#### Paiement Mobile Money (M-Pesa)
```bash
POST /api/paiements/enregistrer
{
  "etudiant_id": 1,
  "montant": 150000,
  "devise": "CDF",
  "type_frais": "Minerval 1er trimestre",
  "mode_paiement": "mpesa",
  "numero_telephone": "+243999999999",
  "nom_expediteur": "Parent Nom"
}
```

#### Paiement Especes
```bash
POST /api/paiements/enregistrer
{
  "etudiant_id": 1,
  "montant": 150000,
  "devise": "CDF",
  "type_frais": "Minerval 1er trimestre",
  "mode_paiement": "especes",
  "numero_bordereau": "BOR-2024-001"
}
```

#### Paiement Western Union
```bash
POST /api/paiements/enregistrer
{
  "etudiant_id": 1,
  "montant": 150000,
  "devise": "CDF",
  "type_frais": "Minerval 1er trimestre",
  "mode_paiement": "western_union",
  "code_mtcn": "1234567890",
  "nom_expediteur": "Parent Nom",
  "agence_nom": "Western Union Lubumbashi Centre"
}
```

#### Paiement Banque
```bash
POST /api/paiements/enregistrer
{
  "etudiant_id": 1,
  "montant": 150000,
  "devise": "CDF",
  "type_frais": "Minerval 1er trimestre",
  "mode_paiement": "rawbank",
  "numero_compte": "1234567890",
  "nom_banque": "Rawbank Lubumbashi"
}
```

### 3. Consulter les Moyens de Paiement
```bash
GET /api/paiements/moyens-paiement
```

Retourne tous les moyens disponibles groupes par categorie.

### 4. Historique des Paiements
```bash
GET /api/paiements/historique?etudiant_id=1
GET /api/paiements/historique?mode_paiement=mpesa
GET /api/paiements/historique?date_debut=2024-01-01&date_fin=2024-12-31
```

### 5. Statistiques
```bash
GET /api/paiements/stats/dashboard
```

---

## DEPLOIEMENT SUR RAILWAY

### 1. Preparer le Projet
```bash
git init
git add .
git commit -m "Oasis des Juniors - Initial commit"
```

### 2. Creer Repository GitHub
```bash
git remote add origin https://github.com/votre-username/edupay-oasis.git
git push -u origin main
```

### 3. Deployer sur Railway
1. Aller sur https://railway.app
2. Cliquer "New Project"
3. Selectionner "Deploy from GitHub repo"
4. Choisir votre repository
5. Ajouter PostgreSQL (cliquer "+ New" → "Database" → "PostgreSQL")
6. Configurer les variables d'environnement:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=votre_cle_secrete_32_caracteres_minimum
   ```
7. Deployer!

### 4. Initialiser la DB en Production
```bash
railway run python -m app.init_oasis
```

Votre API sera disponible sur: https://votre-projet.up.railway.app

---

## ENDPOINTS PRINCIPAUX

### Authentification
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Mon profil

### Paiements
- `POST /api/paiements/enregistrer` - Enregistrer paiement
- `GET /api/paiements/moyens-paiement` - Moyens disponibles
- `GET /api/paiements/historique` - Historique
- `GET /api/paiements/{id}` - Details paiement
- `PUT /api/paiements/{id}/valider` - Valider paiement
- `GET /api/paiements/stats/dashboard` - Statistiques

### Etudiants
- `POST /api/etudiants` - Creer etudiant
- `GET /api/etudiants` - Liste etudiants
- `GET /api/etudiants/{id}` - Details etudiant
- `PUT /api/etudiants/{id}` - Modifier etudiant

### Classes
- `GET /api/classes` - Liste classes
- `GET /api/classes/{id}` - Details classe

### Parents
- `POST /api/parents` - Creer parent
- `GET /api/parents` - Liste parents

### Rapports
- `GET /api/rapports/stats/financier` - Stats financieres
- `GET /api/rapports/stats/etudiants` - Stats etudiants

---

## SECURITE

- Authentification JWT
- Mots de passe cryptes (bcrypt)
- Controle d'acces par role
- Audit trail complet
- HTTPS obligatoire en production
- Validation des entrees
- Protection CSRF

---

## SUPPORT

**Complexe Scolaire Oasis des Juniors**
- Adresse: Lubumbashi, RDC
- Telephone: +243 999 999 999
- Email: contact@oasisdesjuniors.cd

**Support Technique**
- Email: support@edupay.cd
- Documentation: http://localhost:8000/docs

---

## LICENCE

Propriete exclusive du Complexe Scolaire Oasis des Juniors
Tous droits reserves - 2024

---

**Fait avec amour a Lubumbashi, RDC**

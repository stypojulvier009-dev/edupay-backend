# GUIDE DEPLOIEMENT RAILWAY - OASIS DES JUNIORS

## ETAPES COMPLETES POUR DEPLOYER

---

## PREPARATION

### 1. Verifier que tout est pret
```bash
cd "E:\mon app\edupay\backend"
dir app\
```

Fichiers necessaires:
- app/main.py ✓
- app/init_oasis.py ✓
- app/middleware.py ✓
- app/models.py ✓
- app/auth.py ✓
- app/routers/* (18 routers) ✓
- Dockerfile ✓
- requirements.txt ✓

---

## DEPLOIEMENT SUR RAILWAY

### 1. Installer Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login Railway
```bash
railway login
```

### 3. Initialiser le projet
```bash
cd "E:\mon app\edupay\backend"
railway init
```

Choisir:
- Create new project
- Nom: edupay-oasis

### 4. Ajouter PostgreSQL
```bash
railway add
```

Choisir: PostgreSQL

### 5. Configurer les variables d'environnement
```bash
railway variables set SECRET_KEY="votre_cle_secrete_ultra_securisee_32_caracteres_minimum"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
railway variables set ENVIRONMENT="production"
```

**IMPORTANT**: Railway injecte automatiquement `DATABASE_URL` depuis PostgreSQL!

### 6. Deployer
```bash
railway up
```

Attendre 2-3 minutes...

### 7. Initialiser la base de donnees
```bash
railway run python -m app.init_oasis
```

Cela va creer:
- L'ecole Oasis des Juniors
- 4 comptes utilisateurs
- 12 classes
- 7 types de frais
- 18 moyens de paiement
- 7 matieres

### 8. Obtenir l'URL
```bash
railway domain
```

Votre API sera disponible sur: `https://edupay-oasis.up.railway.app`

---

## TESTER L'API

### 1. Health Check
```bash
curl https://edupay-oasis.up.railway.app/
```

Reponse:
```json
{
  "message": "EduPay API - Oasis des Juniors",
  "version": "2.0.0",
  "status": "running",
  "features": [...]
}
```

### 2. Login
```bash
curl -X POST https://edupay-oasis.up.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@oasisdesjuniors.cd&password=Admin123!"
```

### 3. Documentation
Ouvrir: `https://edupay-oasis.up.railway.app/docs`

---

## CONFIGURER LE FRONTEND FLUTTER

Modifier `lib/utils/constants.dart`:

```dart
class AppConstants {
  static const String apiBaseUrl = 'https://edupay-oasis.up.railway.app';
  // ...
}
```

Puis:
```bash
cd "E:\mon app\edupay"
flutter pub get
flutter run
```

---

## PROBLEMES COURANTS

### Erreur: "No module named 'app'"
**Solution**: Verifier que vous etes dans le dossier `backend/`

### Erreur: "Table already exists"
**Solution**: La DB est deja initialisee, pas besoin de relancer init_oasis

### Erreur: "Connection refused"
**Solution**: Attendre que le deploiement soit termine (2-3 min)

### Erreur: "No Internet connection"
**Solution**: C'est normal! Le middleware verifie Internet. Desactiver temporairement dans main.py si besoin.

---

## COMMANDES UTILES

### Voir les logs
```bash
railway logs
```

### Voir les variables
```bash
railway variables
```

### Redemarrer
```bash
railway restart
```

### Ouvrir le dashboard
```bash
railway open
```

---

## APRES LE DEPLOIEMENT

### 1. Changer les mots de passe
Se connecter avec admin et changer:
```
PUT /api/auth/me
{
  "mot_de_passe": "nouveau_mot_de_passe_securise"
}
```

### 2. Tester toutes les fonctionnalites
- Login ✓
- Creer etudiant ✓
- Enregistrer paiement ✓
- Voir absents ✓
- Cahier de paiements ✓
- Exports CSV ✓

### 3. Former les utilisateurs
- Admin
- Directeur
- Comptable
- Caissier

---

## COUTS RAILWAY

### Hobby Plan: $5/mois
- 500 heures execution
- 512 MB RAM
- 1 GB stockage
- Parfait pour demarrer!

### Pro Plan: $20/mois
- Execution illimitee
- 8 GB RAM
- 100 GB stockage
- Support prioritaire

---

## BACKUP

### Exporter la base de donnees
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

### Restaurer
```bash
railway run psql $DATABASE_URL < backup.sql
```

---

## MONITORING

### Dashboard Railway
- CPU/RAM usage
- Logs en temps reel
- Metriques requetes
- Alertes automatiques

### Endpoints de monitoring
- GET / - Health check
- GET /health - Status
- GET /docs - Documentation

---

## MISE A JOUR

Pour deployer une nouvelle version:

```bash
git add .
git commit -m "Nouvelle fonctionnalite"
git push origin main
```

Railway redeploie automatiquement!

Ou manuellement:
```bash
railway up
```

---

## SUPPORT

**Railway**
- Dashboard: https://railway.app
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Oasis des Juniors**
- Email: contact@oasisdesjuniors.cd
- Tel: +243 999 999 999

---

## CHECKLIST DEPLOIEMENT

- [ ] Railway CLI installe
- [ ] Login Railway
- [ ] Projet cree
- [ ] PostgreSQL ajoute
- [ ] Variables configurees
- [ ] Code deploye
- [ ] Base de donnees initialisee
- [ ] API testee
- [ ] Frontend configure
- [ ] Mots de passe changes
- [ ] Utilisateurs formes

---

**VOTRE APPLICATION EST EN PRODUCTION! 🚀🇨🇩**

URL: https://edupay-oasis.up.railway.app
Docs: https://edupay-oasis.up.railway.app/docs
Admin: admin@oasisdesjuniors.cd / Admin123!

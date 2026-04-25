# 🚀 Guide de Déploiement EduPay sur Railway

## Prérequis
- Compte GitHub
- Compte Railway (https://railway.app)
- Git installé localement

## Étape 1: Préparer le Repository GitHub

```bash
cd "E:\mon app\edupay"
git init
git add .
git commit -m "Initial commit - EduPay Backend Ultra-Premium"
```

Créez un nouveau repository sur GitHub et poussez le code:
```bash
git remote add origin https://github.com/VOTRE_USERNAME/edupay.git
git branch -M main
git push -u origin main
```

## Étape 2: Déployer sur Railway

### 2.1 Créer un Nouveau Projet
1. Allez sur https://railway.app
2. Cliquez sur "New Project"
3. Sélectionnez "Deploy from GitHub repo"
4. Choisissez votre repository `edupay`

### 2.2 Ajouter PostgreSQL
1. Dans votre projet Railway, cliquez sur "+ New"
2. Sélectionnez "Database" → "PostgreSQL"
3. Railway créera automatiquement la base de données

### 2.3 Configurer les Variables d'Environnement

Dans votre service backend, ajoutez ces variables:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=votre_cle_secrete_ultra_securisee_32_caracteres_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

**IMPORTANT**: Railway injecte automatiquement `DATABASE_URL` depuis PostgreSQL!

### 2.4 Configurer le Déploiement
1. Railway détecte automatiquement le `Dockerfile`
2. Le déploiement démarre automatiquement
3. Attendez 2-3 minutes

## Étape 3: Initialiser la Base de Données

Une fois déployé, exécutez le script d'initialisation:

```bash
# Depuis Railway Dashboard → Service → Shell
python -m app.init_db
```

Cela créera:
- ✅ 4 plans d'abonnement (Gratuit, Basic, Pro, Enterprise)
- ✅ 8 communes de Lubumbashi
- ✅ 30+ quartiers
- ✅ Compte super admin (admin@edupay.cd / Admin123!)

## Étape 4: Tester l'API

Votre API sera disponible à: `https://votre-projet.up.railway.app`

### Test de Santé
```bash
curl https://votre-projet.up.railway.app/
```

### Test de Login
```bash
curl -X POST https://votre-projet.up.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@edupay.cd&password=Admin123!"
```

### Documentation Interactive
Accédez à: `https://votre-projet.up.railway.app/docs`

## Étape 5: Configurer le Frontend Flutter

Mettez à jour `lib/services/api_service.dart`:

```dart
class ApiService {
  static const String baseUrl = 'https://votre-projet.up.railway.app';
  // ... reste du code
}
```

## 🎯 Endpoints Disponibles

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Profil utilisateur

### Abonnements
- `GET /api/abonnements` - Liste des plans
- `POST /api/abonnements/souscrire` - Souscrire
- `GET /api/abonnements/ma-souscription` - Ma souscription

### Géolocalisation
- `GET /api/geo/communes` - Communes de Lubumbashi
- `GET /api/geo/communes/{id}/quartiers` - Quartiers

### Écoles
- `POST /api/ecoles` - Créer école (super_admin)
- `GET /api/ecoles/mon-ecole` - Mon école
- `PUT /api/ecoles/mon-ecole` - Modifier mon école

### Classes
- `POST /api/classes` - Créer classe
- `GET /api/classes` - Liste des classes
- `PUT /api/classes/{id}` - Modifier classe
- `DELETE /api/classes/{id}` - Supprimer classe

### Parents
- `POST /api/parents` - Créer parent
- `GET /api/parents` - Liste des parents
- `GET /api/parents/{id}` - Détails parent
- `PUT /api/parents/{id}` - Modifier parent

### Étudiants
- `POST /api/etudiants` - Créer étudiant
- `GET /api/etudiants` - Liste des étudiants
- `GET /api/etudiants/{id}` - Détails étudiant
- `PUT /api/etudiants/{id}` - Modifier étudiant
- `DELETE /api/etudiants/{id}` - Supprimer étudiant

### Frais Scolaires
- `POST /api/frais` - Créer frais
- `GET /api/frais` - Liste des frais
- `PUT /api/frais/{id}` - Modifier frais

### Échéanciers
- `POST /api/echeanciers` - Créer échéancier
- `GET /api/echeanciers` - Liste des échéanciers
- `POST /api/echeanciers/{id}/tranches` - Créer tranche
- `GET /api/echeanciers/{id}/tranches` - Liste des tranches

### Paiements
- `POST /api/paiements` - Créer paiement
- `GET /api/paiements` - Liste des paiements
- `GET /api/paiements/{id}` - Détails paiement
- `GET /api/paiements/stats/dashboard` - Statistiques

### Notifications
- `POST /api/notifications` - Créer notification
- `GET /api/notifications` - Mes notifications
- `PUT /api/notifications/{id}/lire` - Marquer comme lu

### Rapports
- `POST /api/rapports/generer` - Générer rapport
- `GET /api/rapports` - Liste des rapports
- `GET /api/rapports/stats/financier` - Stats financières
- `GET /api/rapports/stats/etudiants` - Stats étudiants

### Audit
- `POST /api/audit` - Créer log audit
- `GET /api/audit` - Logs d'audit

## 🔒 Sécurité

### Authentification JWT
Tous les endpoints (sauf `/`, `/docs`, `/auth/login`, `/auth/register`) nécessitent un token JWT:

```
Authorization: Bearer <votre_token>
```

### Rôles et Permissions
- `super_admin` - Accès total
- `admin_ecole` - Gestion de son école
- `directeur` - Gestion académique
- `comptable` - Gestion financière
- `caissier` - Enregistrement paiements
- `enseignant` - Consultation
- `parent` - Consultation enfants

## 📊 Monitoring

### Railway Dashboard
- CPU/RAM usage
- Logs en temps réel
- Métriques de requêtes
- Alertes automatiques

### Logs
```bash
# Voir les logs en temps réel
railway logs --follow
```

## 🔄 Mises à Jour

Pour déployer une nouvelle version:

```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin main
```

Railway redéploie automatiquement! 🎉

## 💰 Coûts Railway

- **Hobby Plan**: $5/mois
  - 500 heures d'exécution
  - 512 MB RAM
  - 1 GB stockage
  - Parfait pour démarrer!

- **Pro Plan**: $20/mois
  - Exécution illimitée
  - 8 GB RAM
  - 100 GB stockage
  - Support prioritaire

## 🆘 Dépannage

### Erreur de connexion DB
```bash
# Vérifier DATABASE_URL
railway variables
```

### Erreur de démarrage
```bash
# Voir les logs
railway logs
```

### Réinitialiser la DB
```bash
railway run python -m app.init_db
```

## 🎉 Félicitations!

Votre backend EduPay ultra-premium est maintenant déployé et prêt à générer des millions! 💰🚀

**URL de l'API**: https://votre-projet.up.railway.app
**Documentation**: https://votre-projet.up.railway.app/docs
**Admin**: admin@edupay.cd / Admin123!

---

**Support**: contact@edupay.cd
**Documentation**: https://docs.edupay.cd

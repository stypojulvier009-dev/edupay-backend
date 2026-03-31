require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Base de données
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

pool.on('connect', () => console.log('✅ Connecté à PostgreSQL (Neon)'));
pool.on('error', (err) => console.error('❌ Erreur DB:', err));

// ========== ROUTES PUBLIQUES ==========
const authRoutes = require('./routes/authRoutes');
app.use('/api/auth', authRoutes);

// ========== MIDDLEWARE D'AUTHENTIFICATION ==========
const auth = require('./middleware/auth');

// ========== ROUTES PROTÉGÉES ==========
const studentRoutes = require('./routes/studentRoutes');
const paymentRoutes = require('./routes/paymentRoutes');
const userRoutes = require('./routes/userRoutes');
const classRoutes = require('./routes/classRoutes');
const statsRoutes = require('./routes/statsRoutes');
const adminRoutes = require('./routes/adminRoutes');

app.use('/api/students', auth, studentRoutes);
app.use('/api/payments', auth, paymentRoutes);
app.use('/api/users', auth, userRoutes);
app.use('/api/classes', auth, classRoutes);
app.use('/api/stats', auth, statsRoutes);

// Routes admin (avec vérification du rôle)
const isAdmin = require('./middleware/isAdmin');
app.use('/api/admin', auth, isAdmin, adminRoutes);

// ========== HEALTH CHECK ==========
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'EduPay API is running', database: 'configured' });
});

app.get('/', (req, res) => {
    res.json({ name: 'EduPay API', version: '2.0.0', status: 'online' });
});

// ========== 404 ==========
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route non trouvée' });
});

// ========== GESTION DES ERREURS ==========
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Erreur interne du serveur' });
});

// ========== DÉMARRAGE ==========
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
});

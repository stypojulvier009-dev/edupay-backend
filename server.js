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

// Routes publiques
const authRoutes = require('./routes/authRoutes');
app.use('/api/auth', authRoutes);

// Middleware d'authentification
const auth = require('./middleware/auth');

// Routes protégées
const studentRoutes = require('./routes/studentRoutes');
const paymentRoutes = require('./routes/paymentRoutes');
const userRoutes = require('./routes/userRoutes');
const classRoutes = require('./routes/classRoutes');
const statsRoutes = require('./routes/statsRoutes');

app.use('/api/students', auth, studentRoutes);
app.use('/api/payments', auth, paymentRoutes);
app.use('/api/users', auth, userRoutes);
app.use('/api/classes', auth, classRoutes);
app.use('/api/stats', auth, statsRoutes);

// Routes admin (si vous avez un middleware isAdmin)
const adminRoutes = require('./routes/adminRoutes');
const isAdmin = require('./middleware/isAdmin');
app.use('/api/admin', auth, isAdmin, adminRoutes);

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'EduPay API is running', database: 'configured' });
});

app.get('/', (req, res) => {
    res.json({ name: 'EduPay API', version: '2.0.0', status: 'online' });
});

// 404
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route non trouvée' });
});

// Gestion des erreurs
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Erreur interne du serveur' });
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
});

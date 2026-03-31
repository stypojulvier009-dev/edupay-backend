require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();

// ========== MIDDLEWARE ==========
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ========== BASE DE DONNÉES ==========
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

pool.on('connect', () => console.log('✅ Connecté à PostgreSQL (Neon)'));
pool.on('error', (err) => console.error('❌ Erreur DB:', err));

// ========== ROUTES PUBLIQUES ==========
const authRoutes = require('./routes/authRoutes');
app.use('/api/auth', authRoutes);

// ========== ROUTES PROTÉGÉES ==========
const auth = require('./middleware/auth');
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
app.use('/api/admin', auth, require('./middleware/isAdmin'), adminRoutes);

// ========== HEALTH CHECK ==========
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'EduPay API is running', timestamp: new Date().toISOString() });
});

app.get('/', (req, res) => {
  res.json({ name: 'EduPay API', version: '2.0.0', status: 'online' });
});

// ========== 404 ==========
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route non trouvée' });
});

// ========== DÉMARRAGE ==========
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
});

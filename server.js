require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(express.json());

// Connexion directe à la base de données
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

// Route d'inscription directe
app.post('/api/auth/register', async (req, res) => {
    const { name, phone, password, matricule } = req.body;
    
    try {
        const bcrypt = require('bcryptjs');
        const jwt = require('jsonwebtoken');
        
        const hashedPassword = await bcrypt.hash(password, 10);
        
        const result = await pool.query(
            `INSERT INTO users (name, phone, pin_hash, matricule) 
             VALUES ($1, $2, $3, $4) 
             RETURNING id, name, phone, matricule`,
            [name, phone, hashedPassword, matricule || null]
        );
        
        const token = jwt.sign(
            { id: result.rows[0].id },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({ success: true, token, user: result.rows[0] });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

// Route de connexion directe
app.post('/api/auth/login', async (req, res) => {
    const { phone, password } = req.body;
    
    try {
        const bcrypt = require('bcryptjs');
        const jwt = require('jsonwebtoken');
        
        const result = await pool.query(
            'SELECT * FROM users WHERE phone = $1',
            [phone]
        );
        
        if (result.rows.length === 0) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }
        
        const user = result.rows[0];
        const valid = await bcrypt.compare(password, user.pin_hash);
        
        if (!valid) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }
        
        const token = jwt.sign(
            { id: user.id },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({ success: true, token, user: { id: user.id, name: user.name, phone: user.phone } });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'EduPay API is running' });
});

app.get('/', (req, res) => {
    res.json({ name: 'EduPay API', version: '1.0.0' });
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Server running on port ${PORT}`);
});require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

// Routes
const authRoutes = require('./routes/authRoutes');

app.use('/api/auth', authRoutes);

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'EduPay API is running',
        timestamp: new Date().toISOString()
    });
});

app.get('/', (req, res) => {
    res.json({ 
        name: 'EduPay API', 
        version: '1.0.0',
        status: 'online'
    });
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
});

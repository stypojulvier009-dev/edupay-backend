require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration PostgreSQL - utiliser DATABASE_URL directement
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
    }
});

// Tester la connexion
pool.connect((err, client, release) => {
    if (err) {
        console.error('❌ Erreur de connexion à PostgreSQL:', err.message);
    } else {
        console.log('✅ Connecté à PostgreSQL sur Neon');
        release();
    }
});

// Route de test
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'EduPay API is running',
        database: process.env.DATABASE_URL ? 'configured' : 'missing'
    });
});

// Route racine
app.get('/', (req, res) => {
    res.json({ 
        name: 'EduPay API', 
        version: '1.0.0',
        status: 'online'
    });
});

// Inscription
app.post('/api/auth/register', async (req, res) => {
    const { name, phone, password, matricule } = req.body;
    
    try {
        const bcrypt = require('bcryptjs');
        const jwt = require('jsonwebtoken');
        
        // Vérifier si l'utilisateur existe
        const existing = await pool.query(
            'SELECT * FROM users WHERE phone = $1',
            [phone]
        );
        
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'Ce numéro est déjà utilisé' });
        }
        
        // Hasher le mot de passe
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Créer l'utilisateur
        const result = await pool.query(
            `INSERT INTO users (name, phone, pin_hash, matricule) 
             VALUES ($1, $2, $3, $4) 
             RETURNING id, name, phone, matricule`,
            [name, phone, hashedPassword, matricule || null]
        );
        
        // Générer le token
        const token = jwt.sign(
            { id: result.rows[0].id, phone: phone },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({ 
            success: true, 
            token, 
            user: result.rows[0] 
        });
    } catch (error) {
        console.error('Register error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Connexion
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
            { id: user.id, phone: phone },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({ 
            success: true, 
            token, 
            user: { 
                id: user.id, 
                name: user.name, 
                phone: user.phone,
                matricule: user.matricule
            } 
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
    console.log(`📊 Base de données: ${process.env.DATABASE_URL ? 'configurée' : 'MANQUANTE'}`);
});

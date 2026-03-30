const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../database/db');

// Inscription
exports.register = async (req, res) => {
    const { name, phone, password, matricule } = req.body;
    
    console.log('📝 Tentative inscription:', { name, phone });

    try {
        // Vérifier si l'utilisateur existe
        const existingUser = await pool.query(
            'SELECT * FROM users WHERE phone = $1',
            [phone]
        );

        if (existingUser.rows.length > 0) {
            return res.status(400).json({ error: 'Ce numéro est déjà utilisé' });
        }

        // Hasher le mot de passe
        const hashedPassword = await bcrypt.hash(password, 10);

        // Créer l'utilisateur
        const newUser = await pool.query(
            `INSERT INTO users (name, phone, pin_hash, matricule) 
             VALUES ($1, $2, $3, $4) 
             RETURNING id, name, phone, matricule`,
            [name, phone, hashedPassword, matricule || null]
        );

        // Générer le token
        const token = jwt.sign(
            { id: newUser.rows[0].id, phone: phone, name: name },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        console.log('✅ Inscription réussie:', phone);
        
        res.json({
            success: true,
            token,
            user: newUser.rows[0]
        });
    } catch (error) {
        console.error('❌ Erreur inscription:', error);
        res.status(500).json({ error: 'Erreur lors de l\'inscription' });
    }
};

// Connexion
exports.login = async (req, res) => {
    const { phone, password } = req.body;
    
    console.log('🔐 Tentative connexion:', { phone });

    try {
        const user = await pool.query(
            'SELECT * FROM users WHERE phone = $1',
            [phone]
        );

        if (user.rows.length === 0) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }

        const validPassword = await bcrypt.compare(password, user.rows[0].pin_hash);
        if (!validPassword) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }

        const token = jwt.sign(
            { id: user.rows[0].id, phone: phone, name: user.rows[0].name },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        console.log('✅ Connexion réussie:', phone);
        
        res.json({
            success: true,
            token,
            user: {
                id: user.rows[0].id,
                name: user.rows[0].name,
                phone: user.rows[0].phone,
                matricule: user.rows[0].matricule
            }
        });
    } catch (error) {
        console.error('❌ Erreur connexion:', error);
        res.status(500).json({ error: 'Erreur lors de la connexion' });
    }
};

const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const pool = require('../database/db');

// Profil utilisateur
router.get('/profile', auth, async (req, res) => {
    try {
        const user = await pool.query(
            `SELECT id, name, phone, email, matricule, role, created_at 
             FROM users WHERE id = $1`,
            [req.user.id]
        );
        if (user.rows.length === 0) {
            return res.status(404).json({ error: 'Utilisateur non trouvé' });
        }
        res.json(user.rows[0]);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement du profil' });
    }
});

// Mettre à jour le profil
router.put('/profile', auth, async (req, res) => {
    const { name, email } = req.body;
    try {
        const result = await pool.query(
            `UPDATE users 
             SET name = COALESCE($1, name),
                 email = COALESCE($2, email)
             WHERE id = $3
             RETURNING id, name, phone, email, matricule, role`,
            [name, email, req.user.id]
        );
        res.json(result.rows[0]);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la mise à jour' });
    }
});

module.exports = router;

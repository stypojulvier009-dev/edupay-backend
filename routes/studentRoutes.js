const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const pool = require('../database/db');

// Récupérer les étudiants du parent connecté
router.get('/', auth, async (req, res) => {
    try {
        const result = await pool.query(
            'SELECT * FROM students WHERE parent_id = $1 ORDER BY name',
            [req.user.id]
        );
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des étudiants' });
    }
});

module.exports = router;

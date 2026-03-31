const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const pool = require('../database/db');

// Récupérer toutes les classes
router.get('/', auth, async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM classes ORDER BY level');
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des classes' });
    }
});

module.exports = router;

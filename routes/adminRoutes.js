const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const isAdmin = require('../middleware/isAdmin');
const pool = require('../database/db');

// Tous les étudiants (admin)
router.get('/students', auth, isAdmin, async (req, res) => {
    try {
        const result = await pool.query(
            `SELECT s.*, u.name as parent_name 
             FROM students s
             LEFT JOIN users u ON s.parent_id = u.id
             ORDER BY s.created_at DESC`
        );
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des étudiants' });
    }
});

// Paiements en attente
router.get('/payments/pending', auth, isAdmin, async (req, res) => {
    try {
        const result = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             WHERE p.status = 'pending'
             ORDER BY p.payment_date DESC`
        );
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des paiements en attente' });
    }
});

// Valider un paiement
router.put('/payments/:id/validate', auth, isAdmin, async (req, res) => {
    const { id } = req.params;
    try {
        await pool.query(
            `UPDATE payments 
             SET status = 'completed', validated_by = $1, validated_at = NOW()
             WHERE id = $2`,
            [req.user.id, id]
        );
        res.json({ success: true });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la validation' });
    }
});

module.exports = router;

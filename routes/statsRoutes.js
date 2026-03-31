const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const pool = require('../database/db');

// Statistiques du tableau de bord
router.get('/dashboard', auth, async (req, res) => {
    try {
        const payments = await pool.query(
            `SELECT COUNT(*) as total, SUM(amount) as total_amount 
             FROM payments p
             JOIN students s ON p.student_id = s.id
             WHERE s.parent_id = $1`,
            [req.user.id]
        );
        const recent = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             WHERE s.parent_id = $1
             ORDER BY p.payment_date DESC
             LIMIT 5`,
            [req.user.id]
        );
        const wallet = await pool.query(
            'SELECT balance_fc, balance_usd FROM wallets WHERE user_id = $1',
            [req.user.id]
        );
        res.json({
            total_payments: payments.rows[0]?.total || 0,
            total_amount: payments.rows[0]?.total_amount || 0,
            balance_fc: wallet.rows[0]?.balance_fc || 0,
            recent_payments: recent.rows
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des statistiques' });
    }
});

module.exports = router;

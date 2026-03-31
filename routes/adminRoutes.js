const express = require('express');
const router = express.Router();
const pool = require('../database/db');
const Student = require('../models/Student');
const Payment = require('../models/Payment');

// Récupérer tous les élèves (admin)
router.get('/students', async (req, res) => {
    try {
        const students = await Student.getAll();
        res.json(students);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des élèves' });
    }
});

// Ajouter un élève (admin) – avec parent existant par téléphone
router.post('/students', async (req, res) => {
    const { name, class_id, matricule, parent_phone, school_fees } = req.body;
    try {
        const student = await Student.adminCreate({ name, class_id, matricule, parent_phone, school_fees });
        res.json(student);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

// Récupérer les paiements en attente de validation
router.get('/payments/pending', async (req, res) => {
    try {
        const payments = await Payment.getPending();
        res.json(payments);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des paiements en attente' });
    }
});

// Valider un paiement (admin)
router.put('/payments/:id/validate', async (req, res) => {
    const { id } = req.params;
    try {
        const payment = await Payment.validate(id, req.user.id);
        if (!payment) return res.status(404).json({ error: 'Paiement non trouvé' });
        res.json({ success: true, payment });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la validation' });
    }
});

// Récupérer les statistiques globales (admin)
router.get('/stats', async (req, res) => {
    try {
        const totalStudents = await pool.query('SELECT COUNT(*) FROM students');
        const totalPayments = await pool.query('SELECT SUM(amount) FROM payments WHERE status = $1', ['completed']);
        const pendingPayments = await pool.query('SELECT COUNT(*) FROM payments WHERE status = $1', ['pending']);
        res.json({
            total_students: parseInt(totalStudents.rows[0].count),
            total_amount: parseFloat(totalPayments.rows[0].sum || 0),
            pending_payments: parseInt(pendingPayments.rows[0].count)
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des statistiques' });
    }
});

module.exports = router;

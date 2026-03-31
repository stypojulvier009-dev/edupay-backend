const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const isAdmin = require('../middleware/isAdmin');
const pool = require('../database/db');

// Tous les élèves (admin)
router.get('/students', auth, isAdmin, async (req, res) => {
  const result = await pool.query('SELECT * FROM students ORDER BY created_at DESC');
  res.json(result.rows);
});

// Ajouter un élève (admin)
router.post('/students', auth, isAdmin, async (req, res) => {
  const { matricule, name, className, parentPhone, schoolFees } = req.body;
  const result = await pool.query(
    `INSERT INTO students (matricule, name, class_name, parent_phone, school_fees, paid_amount)
     VALUES ($1, $2, $3, $4, $5, 0) RETURNING *`,
    [matricule, name, className, parentPhone, schoolFees]
  );
  res.json(result.rows[0]);
});

// Paiements en attente de validation
router.get('/payments/pending', auth, isAdmin, async (req, res) => {
  const result = await pool.query(
    `SELECT p.*, s.matricule, s.class_name 
     FROM payments p
     JOIN students s ON p.student_id = s.id
     WHERE p.status = 'pending'
     ORDER BY p.created_at DESC`
  );
  res.json(result.rows);
});

// Valider un paiement (admin)
router.put('/payments/:id/validate', auth, isAdmin, async (req, res) => {
  const { id } = req.params;
  await pool.query(
    `UPDATE payments 
     SET status = 'completed', validated_by = $1, validated_at = NOW()
     WHERE id = $2`,
    [req.user.id, id]
  );
  res.json({ success: true });
});

module.exports = router;

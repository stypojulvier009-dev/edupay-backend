const pool = require('../database/db');

// Créer un paiement
exports.createPayment = async (req, res) => {
    const { studentId, studentName, amount, operator, phoneNumber, description } = req.body;
    
    console.log('💰 Paiement reçu:', { studentId, studentName, amount, operator });
    
    try {
        const reference = `${operator.toUpperCase()}${Date.now()}${Math.floor(Math.random() * 1000)}`;
        
        const payment = await pool.query(
            `INSERT INTO payments (student_id, student_name, amount, operator, reference, phone_number, description, status)
             VALUES ($1, $2, $3, $4, $5, $6, $7, 'completed')
             RETURNING *`,
            [studentId, studentName, amount, operator, reference, phoneNumber, description]
        );
        
        // Mettre à jour le montant payé de l'étudiant
        await pool.query(
            `UPDATE students 
             SET paid_amount = paid_amount + $1
             WHERE id = $2`,
            [amount, studentId]
        );
        
        res.json({ 
            success: true, 
            message: 'Paiement effectué avec succès',
            payment: payment.rows[0] 
        });
    } catch (error) {
        console.error('❌ Erreur paiement:', error);
        res.status(500).json({ error: 'Erreur lors du paiement', details: error.message });
    }
};

// Historique des paiements
exports.getHistory = async (req, res) => {
    const { limit = 50, offset = 0 } = req.query;
    
    try {
        const payments = await pool.query(
            `SELECT p.*, s.matricule, s.class_name
             FROM payments p
             LEFT JOIN students s ON p.student_id = s.id
             ORDER BY p.payment_date DESC
             LIMIT $1 OFFSET $2`,
            [parseInt(limit), parseInt(offset)]
        );
        
        res.json(payments.rows);
    } catch (error) {
        console.error('❌ Erreur historique:', error);
        res.status(500).json({ error: 'Erreur lors du chargement de l\'historique' });
    }
};

// Statistiques des paiements
exports.getStats = async (req, res) => {
    try {
        const stats = await pool.query(
            `SELECT 
                operator,
                COUNT(*) as total_payments,
                SUM(amount) as total_amount,
                DATE(payment_date) as date
             FROM payments
             GROUP BY operator, DATE(payment_date)
             ORDER BY date DESC
             LIMIT 30`
        );
        
        res.json(stats.rows);
    } catch (error) {
        console.error('❌ Erreur statistiques:', error);
        res.status(500).json({ error: 'Erreur lors du chargement des statistiques' });
    }
};

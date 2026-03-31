const pool = require('../database/db');

class Payment {
    // Créer un paiement
    static async create(paymentData) {
        const {
            student_id,
            student_name,
            amount,
            operator,
            reference,
            receipt_number,
            phone_number,
            description,
            payment_type_id
        } = paymentData;

        const result = await pool.query(
            `INSERT INTO payments 
             (student_id, student_name, amount, operator, reference, receipt_number, phone_number, description, status, payment_type_id)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed', $9)
             RETURNING *`,
            [student_id, student_name, amount, operator, reference, receipt_number, phone_number, description, payment_type_id]
        );
        return result.rows[0];
    }

    // Récupérer les paiements d'un parent (via ses élèves)
    static async findByParent(parentId, limit = 50, offset = 0) {
        const result = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE s.parent_id = $1
             ORDER BY p.payment_date DESC
             LIMIT $2 OFFSET $3`,
            [parentId, limit, offset]
        );
        return result.rows;
    }

    // Récupérer les paiements d'un étudiant spécifique
    static async findByStudent(studentId) {
        const result = await pool.query(
            `SELECT p.*, pt.name as payment_type_name
             FROM payments p
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE p.student_id = $1
             ORDER BY p.payment_date DESC`,
            [studentId]
        );
        return result.rows;
    }

    // Récupérer un paiement par son ID (avec infos élève)
    static async findById(paymentId) {
        const result = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE p.id = $1`,
            [paymentId]
        );
        return result.rows[0];
    }

    // Récupérer tous les paiements (admin)
    static async getAll(limit = 100, offset = 0) {
        const result = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, u.name as parent_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             JOIN users u ON s.parent_id = u.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             ORDER BY p.payment_date DESC
             LIMIT $1 OFFSET $2`,
            [limit, offset]
        );
        return result.rows;
    }

    // Récupérer les paiements en attente de validation
    static async getPending() {
        const result = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, u.name as parent_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             JOIN users u ON s.parent_id = u.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE p.status = 'pending'
             ORDER BY p.payment_date DESC`
        );
        return result.rows;
    }

    // Valider un paiement (admin)
    static async validate(paymentId, adminId) {
        const result = await pool.query(
            `UPDATE payments 
             SET status = 'completed', validated_by = $1, validated_at = NOW()
             WHERE id = $2 AND status = 'pending'
             RETURNING *`,
            [adminId, paymentId]
        );
        return result.rows[0];
    }

    // Annuler un paiement (admin)
    static async cancel(paymentId, adminId, reason) {
        const result = await pool.query(
            `UPDATE payments 
             SET status = 'cancelled', validated_by = $1, validated_at = NOW(), description = COALESCE(description, '') || '\nAnnulation: ' || $2
             WHERE id = $3 AND status = 'pending'
             RETURNING *`,
            [adminId, reason, paymentId]
        );
        return result.rows[0];
    }

    // Récupérer les statistiques de paiements pour un parent
    static async getStatsForParent(parentId) {
        const result = await pool.query(
            `SELECT 
                COUNT(*) as total_payments,
                SUM(amount) as total_amount,
                operator,
                DATE_TRUNC('month', payment_date) as month
             FROM payments p
             JOIN students s ON p.student_id = s.id
             WHERE s.parent_id = $1
             GROUP BY operator, DATE_TRUNC('month', payment_date)
             ORDER BY month DESC`,
            [parentId]
        );
        return result.rows;
    }

    // Récupérer les statistiques globales (admin)
    static async getGlobalStats() {
        const result = await pool.query(
            `SELECT 
                COUNT(*) as total_payments,
                SUM(amount) as total_amount,
                operator,
                status,
                DATE_TRUNC('month', payment_date) as month
             FROM payments
             GROUP BY operator, status, DATE_TRUNC('month', payment_date)
             ORDER BY month DESC`
        );
        return result.rows;
    }

    // Récupérer le montant total payé par étudiant
    static async getTotalPaidByStudent(studentId) {
        const result = await pool.query(
            `SELECT SUM(amount) as total_paid
             FROM payments
             WHERE student_id = $1 AND status = 'completed'`,
            [studentId]
        );
        return parseFloat(result.rows[0].total_paid || 0);
    }

    // Générer un numéro de reçu unique
    static async generateReceiptNumber() {
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 10000);
        return `REC-${timestamp}-${random}`;
    }

    // Vérifier si une référence existe déjà
    static async referenceExists(reference) {
        const result = await pool.query(
            'SELECT id FROM payments WHERE reference = $1',
            [reference]
        );
        return result.rows.length > 0;
    }

    // Récupérer les paiements par période
    static async getByDateRange(startDate, endDate, parentId = null) {
        let query = `
            SELECT p.*, s.name as student_name, s.class_name
            FROM payments p
            JOIN students s ON p.student_id = s.id
            WHERE p.payment_date BETWEEN $1 AND $2
        `;
        const params = [startDate, endDate];
        
        if (parentId) {
            query += ` AND s.parent_id = $3`;
            params.push(parentId);
        }
        
        query += ` ORDER BY p.payment_date DESC`;
        
        const result = await pool.query(query, params);
        return result.rows;
    }
}

module.exports = Payment;

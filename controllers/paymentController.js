const pool = require('../database/db');
const Student = require('../models/Student');

// Effectuer un paiement
exports.createPayment = async (req, res) => {
    const { studentId, studentName, amount, operator, phoneNumber, description, paymentTypeId } = req.body;

    const client = await pool.connect();
    try {
        await client.query('BEGIN');

        // Vérifier que l'élève appartient bien au parent
        const student = await Student.findByIdAndParent(studentId, req.user.id);
        if (!student) {
            return res.status(403).json({ error: 'Accès non autorisé à cet élève' });
        }

        // Générer un numéro de reçu unique
        const receiptNumber = `REC-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        const reference = `PAY-${Date.now()}-${Math.floor(Math.random() * 10000)}`;

        const payment = await client.query(
            `INSERT INTO payments (student_id, student_name, amount, operator, reference, receipt_number, phone_number, description, status, payment_type_id)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed', $9)
             RETURNING *`,
            [studentId, studentName, amount, operator, reference, receiptNumber, phoneNumber, description, paymentTypeId]
        );

        // Mettre à jour le montant payé de l'élève
        await Student.updatePayment(studentId, amount);

        // Enregistrer la transaction
        await client.query(
            `INSERT INTO transactions (user_id, amount_fc, type, status, provider, phone_number, reference, description)
             VALUES ($1, $2, 'payment', 'completed', $3, $4, $5, $6)`,
            [req.user.id, amount, operator, phoneNumber, reference, description]
        );

        // Créer une notification in-app
        const notificationTitle = 'Paiement réussi';
        const notificationMessage = `Votre paiement de ${amount} FC pour ${studentName} a été effectué avec succès. Reçu: ${receiptNumber}`;
        await client.query(
            `INSERT INTO notifications (user_id, title, message) VALUES ($1, $2, $3)`,
            [req.user.id, notificationTitle, notificationMessage]
        );

        await client.query('COMMIT');

        res.json({
            success: true,
            payment: payment.rows[0],
            receiptNumber
        });
    } catch (error) {
        await client.query('ROLLBACK');
        console.error('Payment error:', error);
        res.status(500).json({ error: 'Erreur lors du paiement' });
    } finally {
        client.release();
    }
};

// Récupérer les élèves du parent
exports.getStudents = async (req, res) => {
    try {
        const students = await Student.findByParent(req.user.id);
        res.json(students);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des élèves' });
    }
};

// Récupérer les types de frais
exports.getPaymentTypes = async (req, res) => {
    try {
        const types = await pool.query('SELECT * FROM payment_types ORDER BY id');
        res.json(types.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des types de frais' });
    }
};

// Générer un reçu PDF
exports.getReceipt = async (req, res) => {
    const { paymentId } = req.params;
    try {
        const payment = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE p.id = $1 AND s.parent_id = $2`,
            [paymentId, req.user.id]
        );
        if (payment.rows.length === 0) return res.status(404).json({ error: 'Reçu non trouvé' });
        const data = payment.rows[0];

        // Génération HTML simple (pour l’instant, on renvoie une vue HTML)
        // Pour un vrai PDF, installez pdfmake et générez un PDF.
        const html = `
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><title>Reçu ${data.receipt_number}</title></head>
            <body style="font-family: sans-serif;">
                <h1>ECOLEX SCOLAIRE OASIS DES JUNIORS</h1>
                <h2>Reçu de paiement</h2>
                <p><strong>Réf:</strong> ${data.receipt_number}</p>
                <p><strong>Date:</strong> ${new Date(data.payment_date).toLocaleDateString('fr-FR')}</p>
                <p><strong>Élève:</strong> ${data.student_name} (${data.class_name})</p>
                <p><strong>Type:</strong> ${data.payment_type_name || 'Frais scolaire'}</p>
                <p><strong>Montant:</strong> ${data.amount} FC</p>
                <p><strong>Opérateur:</strong> ${data.operator}</p>
                <p><strong>Statut:</strong> ${data.status}</p>
                <hr>
                <p>Merci de votre confiance !</p>
            </body>
            </html>
        `;
        res.setHeader('Content-Type', 'text/html');
        res.send(html);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la génération du reçu' });
    }
};

// Récupérer les notifications
exports.getNotifications = async (req, res) => {
    try {
        const notifications = await pool.query(
            'SELECT * FROM notifications WHERE user_id = $1 ORDER BY created_at DESC LIMIT 50',
            [req.user.id]
        );
        res.json(notifications.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des notifications' });
    }
};

// Marquer une notification comme lue
exports.markNotificationRead = async (req, res) => {
    const { id } = req.params;
    try {
        await pool.query(
            'UPDATE notifications SET is_read = true WHERE id = $1 AND user_id = $2',
            [id, req.user.id]
        );
        res.json({ success: true });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors de la mise à jour' });
    }
};

// Historique des paiements
exports.getHistory = async (req, res) => {
    try {
        const payments = await pool.query(
            `SELECT p.*, s.name as student_name, s.class_name, pt.name as payment_type_name
             FROM payments p
             JOIN students s ON p.student_id = s.id
             LEFT JOIN payment_types pt ON p.payment_type_id = pt.id
             WHERE s.parent_id = $1
             ORDER BY p.payment_date DESC
             LIMIT 50`,
            [req.user.id]
        );
        res.json(payments.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement de l\'historique' });
    }
};

// Statistiques
exports.getStats = async (req, res) => {
    try {
        const stats = await pool.query(
            `SELECT 
                operator,
                COUNT(*) as total_payments,
                SUM(amount) as total_amount
             FROM payments p
             JOIN students s ON p.student_id = s.id
             WHERE s.parent_id = $1
             GROUP BY operator`,
            [req.user.id]
        );
        res.json(stats.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erreur lors du chargement des statistiques' });
    }
};

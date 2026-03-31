const pool = require('../database/db');

class Student {
    static async findByParent(parentId) {
        const result = await pool.query(
            `SELECT s.*, c.name as class_name, c.level, c.cycle
             FROM students s
             LEFT JOIN classes c ON s.class_id = c.id
             WHERE s.parent_id = $1
             ORDER BY s.name`,
            [parentId]
        );
        return result.rows;
    }

    static async create({ parent_id, name, class_id, matricule, school_fees }) {
        const result = await pool.query(
            `INSERT INTO students (parent_id, name, class_id, matricule, school_fees, paid_amount)
             VALUES ($1, $2, $3, $4, $5, 0)
             RETURNING *`,
            [parent_id, name, class_id, matricule || null, school_fees]
        );
        return result.rows[0];
    }

    static async findByIdAndParent(id, parentId) {
        const result = await pool.query(
            `SELECT s.*, c.name as class_name, c.level, c.cycle
             FROM students s
             LEFT JOIN classes c ON s.class_id = c.id
             WHERE s.id = $1 AND s.parent_id = $2`,
            [id, parentId]
        );
        return result.rows[0];
    }

    static async updatePayment(id, amount) {
        const result = await pool.query(
            `UPDATE students SET paid_amount = paid_amount + $1, updated_at = NOW() WHERE id = $2 RETURNING *`,
            [amount, id]
        );
        return result.rows[0];
    }

    // Admin : récupérer tous les élèves
    static async getAll() {
        const result = await pool.query(
            `SELECT s.*, u.name as parent_name, c.name as class_name
             FROM students s
             JOIN users u ON s.parent_id = u.id
             LEFT JOIN classes c ON s.class_id = c.id
             ORDER BY s.created_at DESC`
        );
        return result.rows;
    }

    // Admin : ajouter un élève (avec parent existant)
    static async adminCreate({ name, class_id, matricule, parent_phone, school_fees }) {
        // Trouver le parent par téléphone
        const parent = await pool.query('SELECT id FROM users WHERE phone = $1', [parent_phone]);
        if (parent.rows.length === 0) throw new Error('Parent non trouvé');
        const parent_id = parent.rows[0].id;

        const result = await pool.query(
            `INSERT INTO students (parent_id, name, class_id, matricule, school_fees, paid_amount)
             VALUES ($1, $2, $3, $4, $5, 0)
             RETURNING *`,
            [parent_id, name, class_id, matricule || null, school_fees]
        );
        return result.rows[0];
    }
}

module.exports = Student;

const pool = require('../database/db');

class Student {
    static async findByParent(parentId) {
        const result = await pool.query(
            'SELECT * FROM students WHERE parent_id = $1 ORDER BY name',
            [parentId]
        );
        return result.rows;
    }

    static async create({ parent_id, name, class_name, matricule, school_fees }) {
        const result = await pool.query(
            `INSERT INTO students (parent_id, name, class_name, matricule, school_fees, paid_amount)
             VALUES ($1, $2, $3, $4, $5, 0)
             RETURNING *`,
            [parent_id, name, class_name, matricule || null, school_fees]
        );
        return result.rows[0];
    }

    static async findByIdAndParent(id, parentId) {
        const result = await pool.query(
            'SELECT * FROM students WHERE id = $1 AND parent_id = $2',
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
}

module.exports = Student;

const pool = require('../database/db');

class Class {
    static async getAll() {
        const result = await pool.query('SELECT * FROM classes ORDER BY level, name');
        return result.rows;
    }

    static async getById(id) {
        const result = await pool.query('SELECT * FROM classes WHERE id = $1', [id]);
        return result.rows[0];
    }

    static async create({ name, level, cycle, school_fees }) {
        const result = await pool.query(
            `INSERT INTO classes (name, level, cycle, school_fees)
             VALUES ($1, $2, $3, $4)
             RETURNING *`,
            [name, level, cycle, school_fees]
        );
        return result.rows[0];
    }

    static async update(id, { name, level, cycle, school_fees }) {
        const result = await pool.query(
            `UPDATE classes
             SET name = $1, level = $2, cycle = $3, school_fees = $4, updated_at = NOW()
             WHERE id = $5
             RETURNING *`,
            [name, level, cycle, school_fees, id]
        );
        return result.rows[0];
    }

    static async delete(id) {
        await pool.query('DELETE FROM classes WHERE id = $1', [id]);
    }
}

module.exports = Class;

const pool = require('../database/db');

class User {
    static async create({ name, phone, pin_hash, matricule, role = 'parent' }) {
        const result = await pool.query(
            `INSERT INTO users (name, phone, pin_hash, matricule, role) 
             VALUES ($1, $2, $3, $4, $5) 
             RETURNING id, name, phone, matricule, role, created_at`,
            [name, phone, pin_hash, matricule || null, role]
        );
        return result.rows[0];
    }

    static async findByPhone(phone) {
        const result = await pool.query(
            `SELECT id, name, phone, matricule, pin_hash, role, is_verified, created_at 
             FROM users WHERE phone = $1`,
            [phone]
        );
        return result.rows[0];
    }

    static async findByMatricule(matricule) {
        const result = await pool.query(
            `SELECT id, name, phone, matricule, pin_hash, role 
             FROM users WHERE matricule = $1`,
            [matricule]
        );
        return result.rows[0];
    }

    static async findById(id) {
        const result = await pool.query(
            `SELECT id, name, phone, matricule, role, is_verified, created_at 
             FROM users WHERE id = $1`,
            [id]
        );
        return result.rows[0];
    }

    static async update(id, { name, email }) {
        const result = await pool.query(
            `UPDATE users 
             SET name = COALESCE($1, name),
                 email = COALESCE($2, email)
             WHERE id = $3
             RETURNING id, name, phone, email, matricule, role`,
            [name, email, id]
        );
        return result.rows[0];
    }

    static async isAdmin(userId) {
        const result = await pool.query(`SELECT role FROM users WHERE id = $1`, [userId]);
        return result.rows[0]?.role === 'admin';
    }
}

module.exports = User;

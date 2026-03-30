const pool = require('../config/database');

class User {
  static async findByPhone(phone) {
    const result = await pool.query('SELECT * FROM users WHERE phone = $1', [phone]);
    return result.rows[0];
  }

  static async findByMatricule(matricule) {
    const result = await pool.query('SELECT * FROM users WHERE matricule = $1', [matricule]);
    return result.rows[0];
  }

  static async create({ name, phone, matricule, pin_hash }) {
    const result = await pool.query(
      'INSERT INTO users (name, phone, matricule, pin_hash) VALUES ($1, $2, $3, $4) RETURNING id, name, phone, matricule',
      [name, phone, matricule, pin_hash]
    );
    return result.rows[0];
  }
}

module.exports = User;
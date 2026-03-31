const pool = require('../database/db');

class Student {
  static async create({ matricule, name, className, parentPhone, schoolFees }) {
    const result = await pool.query(
      `INSERT INTO students (matricule, name, class_name, parent_phone, school_fees, paid_amount)
       VALUES ($1, $2, $3, $4, $5, 0) RETURNING *`,
      [matricule, name, className, parentPhone, schoolFees]
    );
    return result.rows[0];
  }

  static async findByParent(phone) {
    const result = await pool.query(
      `SELECT * FROM students WHERE parent_phone = $1 ORDER BY created_at DESC`,
      [phone]
    );
    return result.rows;
  }

  static async findById(id) {
    const result = await pool.query(`SELECT * FROM students WHERE id = $1`, [id]);
    return result.rows[0];
  }

  static async updatePayment(id, amount) {
    const result = await pool.query(
      `UPDATE students SET paid_amount = paid_amount + $1 WHERE id = $2 RETURNING *`,
      [amount, id]
    );
    return result.rows[0];
  }
}

module.exports = Student;

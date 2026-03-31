const pool = require('../database/db');

class Payment {
  static async create({ student_id, student_name, amount, operator, reference, phone_number, description }) {
    const result = await pool.query(
      `INSERT INTO payments (student_id, student_name, amount, operator, reference, phone_number, description, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending') RETURNING *`,
      [student_id, student_name, amount, operator, reference, phone_number, description]
    );
    return result.rows[0];
  }

  static async findByParent(phone, limit = 50, offset = 0) {
    const result = await pool.query(
      `SELECT p.*, s.matricule, s.class_name
       FROM payments p
       JOIN students s ON p.student_id = s.id
       WHERE s.parent_phone = $1
       ORDER BY p.payment_date DESC
       LIMIT $2 OFFSET $3`,
      [phone, limit, offset]
    );
    return result.rows;
  }

  static async validate(id, adminId) {
    const result = await pool.query(
      `UPDATE payments SET status = 'completed', validated_by = $1, validated_at = NOW()
       WHERE id = $2 RETURNING *`,
      [adminId, id]
    );
    return result.rows[0];
  }
}

module.exports = Payment;

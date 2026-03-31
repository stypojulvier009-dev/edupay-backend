static async getPending() {
    const result = await pool.query(
        `SELECT p.*, s.name as student_name, s.class_name
         FROM payments p
         JOIN students s ON p.student_id = s.id
         WHERE p.status = 'pending'
         ORDER BY p.payment_date DESC`
    );
    return result.rows;
}

static async validate(id, adminId) {
    const result = await pool.query(
        `UPDATE payments 
         SET status = 'completed', validated_by = $1, validated_at = NOW()
         WHERE id = $2 AND status = 'pending'
         RETURNING *`,
        [adminId, id]
    );
    return result.rows[0];
}

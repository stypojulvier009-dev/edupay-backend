const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const pool = require('../database/db');

router.get('/', auth, async (req, res) => {
  const result = await pool.query('SELECT * FROM classes ORDER BY level');
  res.json(result.rows);
});

module.exports = router;

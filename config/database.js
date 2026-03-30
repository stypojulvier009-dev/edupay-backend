const { Pool } = require('pg');
require('dotenv').config();

console.log('🔍 DB_HOST:', process.env.DB_HOST);
console.log('🔍 DB_PORT:', process.env.DB_PORT);
console.log('🔍 DB_USER:', process.env.DB_USER);
console.log('🔍 DB_NAME:', process.env.DB_NAME);

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: { rejectUnauthorized: false }
});

// Test de connexion
pool.connect()
  .then(client => {
    console.log('✅ PostgreSQL connecté !');
    client.release();
  })
  .catch(err => {
    console.error('❌ PostgreSQL erreur:', err.message);
  });

module.exports = pool;
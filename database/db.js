const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
    }
});

pool.on('connect', () => {
    console.log('✅ Connecté à PostgreSQL sur Neon');
});

pool.on('error', (err) => {
    console.error('❌ Erreur PostgreSQL:', err);
});

module.exports = pool;

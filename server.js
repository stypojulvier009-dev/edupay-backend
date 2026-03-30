const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/wallet', require('./routes/walletRoutes'));
app.use('/api/payment', require('./routes/paymentRoutes'));

// Route de test
app.get('/', (req, res) => {
  res.json({ message: 'API EduPay fonctionne !' });
});

// Démarrer le serveur
app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur démarré sur http://0.0.0.0:${port}`);
});

const pool = require('../config/database');

const paymentController = {
  // Effectuer un paiement
  makePayment: async (req, res) => {
    try {
      const userId = req.user.id;
      const { amount_fc, provider, phone_number, description } = req.body;

      if (!amount_fc || amount_fc <= 0) {
        return res.status(400).json({ message: 'Montant invalide' });
      }

      // Vérifier le solde
      const wallet = await pool.query(
        'SELECT balance_fc FROM wallets WHERE user_id = $1',
        [userId]
      );

      if (wallet.rows[0].balance_fc < amount_fc) {
        return res.status(400).json({ message: 'Solde insuffisant' });
      }

      const amount_usd = amount_fc / process.env.EXCHANGE_RATE;
      const reference = `PAY_${Date.now()}_${userId}`;

      // Débiter le wallet
      await pool.query(
        'UPDATE wallets SET balance_fc = balance_fc - $1, balance_usd = balance_usd - $2, updated_at = NOW() WHERE user_id = $3',
        [amount_fc, amount_usd, userId]
      );

      // Enregistrer la transaction
      await pool.query(
        `INSERT INTO transactions (user_id, amount_fc, amount_usd, type, status, provider, phone_number, reference, description)
         VALUES ($1, $2, $3, 'payment', 'success', $4, $5, $6, $7)`,
        [userId, amount_fc, amount_usd, provider, phone_number, reference, description || 'Paiement effectué']
      );

      res.json({
        success: true,
        message: 'Paiement effectué avec succès',
        data: { amount_fc, amount_usd, reference }
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  },

  // Historique des transactions
  getHistory: async (req, res) => {
    try {
      const userId = req.user.id;
      const { limit = 50, offset = 0 } = req.query;

      const result = await pool.query(
        `SELECT * FROM transactions 
         WHERE user_id = $1 
         ORDER BY created_at DESC 
         LIMIT $2 OFFSET $3`,
        [userId, limit, offset]
      );

      res.json({
        success: true,
        data: result.rows
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  }
};

module.exports = paymentController;
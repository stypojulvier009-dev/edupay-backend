const pool = require('../config/database');

const walletController = {
  // Récupérer le wallet de l'utilisateur
  getWallet: async (req, res) => {
    try {
      const userId = req.user.id;

      const result = await pool.query(
        'SELECT balance_fc, balance_usd, updated_at FROM wallets WHERE user_id = $1',
        [userId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ message: 'Wallet non trouvé' });
      }

      res.json({
        success: true,
        data: result.rows[0]
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  },

  // Ajouter de l'argent au wallet (recharge)
  rechargeWallet: async (req, res) => {
    try {
      const userId = req.user.id;
      const { amount_fc, provider, phone_number } = req.body;

      if (!amount_fc || amount_fc <= 0) {
        return res.status(400).json({ message: 'Montant invalide' });
      }

      // Calculer l'équivalent en USD
      const amount_usd = amount_fc / process.env.EXCHANGE_RATE;

      // Mettre à jour le wallet
      await pool.query(
        'UPDATE wallets SET balance_fc = balance_fc + $1, balance_usd = balance_usd + $2, updated_at = NOW() WHERE user_id = $3',
        [amount_fc, amount_usd, userId]
      );

      // Créer une transaction
      const reference = `RECH_${Date.now()}_${userId}`;
      await pool.query(
        `INSERT INTO transactions (user_id, amount_fc, amount_usd, type, status, provider, phone_number, reference, description)
         VALUES ($1, $2, $3, 'recharge', 'success', $4, $5, $6, 'Recharge de compte')`,
        [userId, amount_fc, amount_usd, provider, phone_number, reference]
      );

      res.json({
        success: true,
        message: 'Recharge effectuée avec succès',
        data: { amount_fc, amount_usd, reference }
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  }
};

module.exports = walletController;
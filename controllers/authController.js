const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../config/database');

const authController = {
  register: async (req, res) => {
    try {
      console.log('📝 Données reçues:', req.body);
      
      const { name, phone, matricule, pin } = req.body;

      if (!name || !phone || !pin) {
        return res.status(400).json({ message: 'Champs manquants: name, phone, pin requis' });
      }

      // Vérifier si l'utilisateur existe déjà
      const existingUser = await pool.query('SELECT * FROM users WHERE phone = $1', [phone]);
      if (existingUser.rows.length > 0) {
        return res.status(400).json({ message: 'Ce numéro est déjà utilisé' });
      }

      // Hasher le PIN
      const salt = await bcrypt.genSalt(10);
      const pin_hash = await bcrypt.hash(pin, salt);

      // Créer l'utilisateur
      const result = await pool.query(
        'INSERT INTO users (name, phone, matricule, pin_hash) VALUES ($1, $2, $3, $4) RETURNING id, name, phone, matricule',
        [name, phone, matricule, pin_hash]
      );
      
      const user = result.rows[0];

      // Générer le token JWT
      const token = jwt.sign(
        { id: user.id, phone: user.phone },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
      );

      res.status(201).json({
        success: true,
        message: 'Utilisateur créé avec succès',
        data: { user, token }
      });
    } catch (error) {
      console.error('❌ Erreur:', error);
      res.status(500).json({ message: 'Erreur serveur', error: error.message });
    }
  },

  login: async (req, res) => {
    try {
      const { phone, pin } = req.body;

      if (!phone || !pin) {
        return res.status(400).json({ message: 'Champs manquants: phone, pin requis' });
      }

      const result = await pool.query('SELECT * FROM users WHERE phone = $1', [phone]);
      const user = result.rows[0];

      if (!user) {
        return res.status(401).json({ message: 'Numéro ou PIN incorrect' });
      }

      const validPin = await bcrypt.compare(pin, user.pin_hash);
      if (!validPin) {
        return res.status(401).json({ message: 'Numéro ou PIN incorrect' });
      }

      const token = jwt.sign(
        { id: user.id, phone: user.phone },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
      );

      res.json({
        success: true,
        message: 'Connexion réussie',
        data: {
          user: {
            id: user.id,
            name: user.name,
            phone: user.phone,
            matricule: user.matricule
          },
          token
        }
      });
    } catch (error) {
      console.error('❌ Erreur:', error);
      res.status(500).json({ message: 'Erreur serveur', error: error.message });
    }
  }
};

module.exports = authController;
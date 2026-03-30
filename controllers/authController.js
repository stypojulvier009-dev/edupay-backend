const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const authController = {
  // Inscription
  register: async (req, res) => {
    try {
      const { name, phone, matricule, pin } = req.body;

      // Vérifier si l'utilisateur existe déjà
      const existingUser = await User.findByPhone(phone);
      if (existingUser) {
        return res.status(400).json({ message: 'Ce numéro est déjà utilisé' });
      }

      // Hasher le PIN
      const salt = await bcrypt.genSalt(10);
      const pin_hash = await bcrypt.hash(pin, salt);

      // Créer l'utilisateur
      const user = await User.create({ name, phone, matricule, pin_hash });

      // Générer le token JWT
      const token = jwt.sign(
        { id: user.id, phone: user.phone },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN }
      );

      res.status(201).json({
        success: true,
        message: 'Utilisateur créé avec succès',
        data: { user, token }
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  },

  // Connexion
  login: async (req, res) => {
    try {
      const { phone, pin } = req.body;

      // Vérifier si l'utilisateur existe
      const user = await User.findByPhone(phone);
      if (!user) {
        return res.status(401).json({ message: 'Numéro ou PIN incorrect' });
      }

      // Vérifier le PIN
      const validPin = await bcrypt.compare(pin, user.pin_hash);
      if (!validPin) {
        return res.status(401).json({ message: 'Numéro ou PIN incorrect' });
      }

      // Générer le token JWT
      const token = jwt.sign(
        { id: user.id, phone: user.phone },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN }
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
      console.error(error);
      res.status(500).json({ message: 'Erreur serveur' });
    }
  }
};

module.exports = authController;
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

exports.register = async (req, res) => {
    const { name, phone, password, matricule } = req.body;
    try {
        // Vérifier si le téléphone existe déjà
        const existingUser = await User.findByPhone(phone);
        if (existingUser) {
            return res.status(400).json({ error: 'Ce numéro est déjà utilisé' });
        }

        // Vérifier le matricule s'il est fourni
        if (matricule && matricule.trim() !== '') {
            const existingMatricule = await User.findByMatricule(matricule.trim());
            if (existingMatricule) {
                return res.status(400).json({ error: 'Ce matricule est déjà utilisé' });
            }
        }

        // Hasher le PIN
        const hashedPassword = await bcrypt.hash(password, 10);

        // Créer l'utilisateur
        const user = await User.create({
            name,
            phone,
            pin_hash: hashedPassword,
            matricule: matricule && matricule.trim() !== '' ? matricule.trim() : null,
            role: 'parent'
        });

        // Générer le token JWT
        const token = jwt.sign(
            { id: user.id, phone: user.phone, name: user.name, role: user.role },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.json({
            success: true,
            token,
            user: {
                id: user.id,
                name: user.name,
                phone: user.phone,
                matricule: user.matricule,
                role: user.role
            }
        });
    } catch (error) {
        console.error('Register error:', error);
        // Gestion des doublons PostgreSQL
        if (error.code === '23505') {
            if (error.constraint === 'users_matricule_key') {
                return res.status(400).json({ error: 'Ce matricule est déjà utilisé' });
            }
            if (error.constraint === 'users_phone_key') {
                return res.status(400).json({ error: 'Ce numéro est déjà utilisé' });
            }
        }
        res.status(500).json({ error: 'Erreur lors de l\'inscription' });
    }
};

exports.login = async (req, res) => {
    const { phone, password } = req.body;
    try {
        const user = await User.findByPhone(phone);
        if (!user) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }

        const validPassword = await bcrypt.compare(password, user.pin_hash);
        if (!validPassword) {
            return res.status(401).json({ error: 'Identifiants invalides' });
        }

        const token = jwt.sign(
            { id: user.id, phone: user.phone, name: user.name, role: user.role },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.json({
            success: true,
            token,
            user: {
                id: user.id,
                name: user.name,
                phone: user.phone,
                matricule: user.matricule,
                role: user.role
            }
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Erreur lors de la connexion' });
    }
};

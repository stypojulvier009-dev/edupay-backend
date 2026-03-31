const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Accès non autorisé' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = {
            id: decoded.id,
            phone: decoded.phone,
            name: decoded.name,
            role: decoded.role
        };
        next();
    } catch (error) {
        console.error('Token verification error:', error.message);
        return res.status(403).json({ error: 'Token invalide' });
    }
};

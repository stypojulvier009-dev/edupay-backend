const express = require('express');
const router = express.Router();
const classController = require('../controllers/classController');
const auth = require('../middleware/auth');
const isAdmin = require('../middleware/isAdmin');

// Routes accessibles à tous les utilisateurs authentifiés (pour l'affichage)
router.get('/', auth, classController.getAllClasses);

// Routes admin
router.post('/', auth, isAdmin, classController.createClass);
router.put('/:id', auth, isAdmin, classController.updateClass);
router.delete('/:id', auth, isAdmin, classController.deleteClass);

module.exports = router;

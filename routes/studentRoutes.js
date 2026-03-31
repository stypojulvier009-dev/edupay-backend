const express = require('express');
const router = express.Router();
const studentController = require('../controllers/studentController');
const auth = require('../middleware/auth');
const isAdmin = require('../middleware/isAdmin');

// Parent
router.get('/', auth, studentController.getMyStudents);
router.post('/', auth, studentController.addMyStudent);

// Admin
router.get('/all', auth, isAdmin, studentController.getAllStudents);
router.post('/admin', auth, isAdmin, studentController.addStudentByAdmin);

module.exports = router;

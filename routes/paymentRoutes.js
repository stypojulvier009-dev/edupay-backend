const express = require('express');
const authMiddleware = require('../middleware/auth');
const paymentController = require('../controllers/paymentController'); // Note: P majuscule

const router = express.Router();

// Routes de paiement
router.post('/', authMiddleware, paymentController.createPayment); // createPayment, pas makePayment
router.get('/history', authMiddleware, paymentController.getHistory);
router.get('/stats', authMiddleware, paymentController.getStats);

module.exports = router;

const express = require('express');
const authMiddleware = require('../middleware/auth');
const paymentController = require('../controllers/paymentController');
const router = express.Router();

router.post('/', authMiddleware, paymentController.makePayment);
router.get('/history', authMiddleware, paymentController.getHistory);

module.exports = router;
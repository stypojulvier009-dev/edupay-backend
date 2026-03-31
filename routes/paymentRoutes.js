const express = require('express');
const router = express.Router();
const paymentController = require('../controllers/paymentController');
const auth = require('../middleware/auth');

router.post('/', auth, paymentController.createPayment);
router.get('/history', auth, paymentController.getHistory);
router.get('/stats', auth, paymentController.getStats);
router.get('/students', auth, paymentController.getStudents);
router.get('/payment-types', auth, paymentController.getPaymentTypes);
router.get('/receipt/:paymentId', auth, paymentController.getReceipt);
router.get('/notifications', auth, paymentController.getNotifications);
router.put('/notifications/:id', auth, paymentController.markNotificationRead);

module.exports = router;

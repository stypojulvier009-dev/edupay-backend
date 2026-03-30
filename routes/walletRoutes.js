const express = require('express');
const authMiddleware = require('../middleware/auth');
const walletController = require('../controllers/walletController');
const router = express.Router();

router.get('/', authMiddleware, walletController.getWallet);
router.post('/recharge', authMiddleware, walletController.rechargeWallet);

module.exports = router;
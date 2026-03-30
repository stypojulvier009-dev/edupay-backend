require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());
app.use(express.json());

// Routes
const authRoutes = require('./routes/authRoutes');

app.use('/api/auth', authRoutes);

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'EduPay API is running',
        timestamp: new Date().toISOString()
    });
});

app.get('/', (req, res) => {
    res.json({ 
        name: 'EduPay API', 
        version: '1.0.0',
        status: 'online'
    });
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`✅ Serveur EduPay démarré sur le port ${PORT}`);
});

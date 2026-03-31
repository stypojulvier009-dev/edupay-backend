// services/notificationService.js
async function sendNotification(userId, title, body) {
    console.log(`Notification pour user ${userId}: ${title} - ${body}`);
    // Ici, vous pouvez intégrer Firebase Cloud Messaging ou un service SMS
}

module.exports = { sendNotification };

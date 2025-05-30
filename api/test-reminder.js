export default async function handler(req, res) {
  // Headers CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // Configuration Pushover
    const PUSHOVER_API_TOKEN = process.env.PUSHOVER_API_TOKEN;
    const PUSHOVER_USER_KEY = process.env.PUSHOVER_USER_KEY;

    if (!PUSHOVER_API_TOKEN || !PUSHOVER_USER_KEY) {
      return res.status(500).json({ error: 'Configuration Pushover manquante' });
    }

    const reminderMessage = `🧪 TEST - N'oubliez pas de partager votre météo intérieure aujourd'hui ! 
    
Rendez-vous sur votre Moodcast pour dire comment vous vous sentez. 💙`;

    // Envoyer notification aux deux appareils
    const notifications = [
      {
        device: 'iphone',    // Appareil de Clémence
        user: 'Clémence'
      },
      {
        device: 'iphoneF',   // Appareil de Franklin
        user: 'Franklin'
      }
    ];

    const results = [];
    
    for (const notification of notifications) {
      try {
        const response = await fetch('https://api.pushover.net/1/messages.json', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            token: PUSHOVER_API_TOKEN,
            user: PUSHOVER_USER_KEY,
            message: reminderMessage,
            title: `TEST - Moodcast Rappel pour ${notification.user}`,
            device: notification.device,
            priority: 0,
            sound: 'pushover'
          })
        });

        const result = await response.json();
        results.push({
          device: notification.device,
          user: notification.user,
          success: response.ok,
          result: result
        });
      } catch (error) {
        results.push({
          device: notification.device,
          user: notification.user,
          success: false,
          error: error.message
        });
      }
    }

    const successCount = results.filter(r => r.success).length;
    
    return res.status(200).json({
      message: `Test des rappels quotidiens`,
      sent: successCount,
      total: notifications.length,
      results: results
    });

  } catch (error) {
    return res.status(500).json({ 
      error: 'Erreur lors du test des rappels',
      details: error.message 
    });
  }
} 
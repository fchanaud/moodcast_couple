module.exports = async (req, res) => {
  // Vérifier que c'est bien un appel cron de Vercel
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Configuration Pushover
    const PUSHOVER_API_TOKEN = process.env.PUSHOVER_API_TOKEN;
    const PUSHOVER_USER_KEY = process.env.PUSHOVER_USER_KEY;

    if (!PUSHOVER_API_TOKEN || !PUSHOVER_USER_KEY) {
      console.log('Configuration Pushover manquante');
      return res.status(500).json({ error: 'Configuration Pushover manquante' });
    }

    // Obtenir la date d'aujourd'hui (UK timezone)
    const today = new Date().toLocaleDateString('en-CA', { 
      timeZone: 'Europe/London' 
    }); // Format YYYY-MM-DD

    // Note: En production, nous ne pouvons pas accéder au localStorage des utilisateurs
    // Cette fonction enverra toujours le rappel car nous ne pouvons pas vérifier
    // si les humeurs ont été partagées (localStorage est côté client)
    
    const reminderMessage = `🌤️ N'oubliez pas de partager votre météo intérieure aujourd'hui ! 
    
Rendez-vous sur votre Moodcast pour dire comment vous vous sentez. 💙`;

    // Envoyer notification aux deux appareils
    const notifications = [
      {
        device: 'iphone',
        user: 'Clémence'
      },
      {
        device: 'iphoneF', 
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
            title: `Moodcast - Rappel pour ${notification.user}`,
            device: notification.device,
            priority: 0, // Priorité normale
            sound: 'pushover' // Son par défaut
          })
        });

        const result = await response.json();
        results.push({
          device: notification.device,
          user: notification.user,
          success: response.ok,
          result: result
        });

        console.log(`Rappel envoyé à ${notification.user} (${notification.device}):`, result);
      } catch (error) {
        console.error(`Erreur envoi rappel à ${notification.user}:`, error);
        results.push({
          device: notification.device,
          user: notification.user,
          success: false,
          error: error.message
        });
      }
    }

    // Retourner le résumé
    const successCount = results.filter(r => r.success).length;
    
    return res.status(200).json({
      message: `Rappels quotidiens envoyés`,
      date: today,
      sent: successCount,
      total: notifications.length,
      results: results
    });

  } catch (error) {
    console.error('Erreur dans le rappel quotidien:', error);
    return res.status(500).json({ 
      error: 'Erreur lors de l\'envoi des rappels',
      details: error.message 
    });
  }
}; 
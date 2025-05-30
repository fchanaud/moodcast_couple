const { createClient } = require('@supabase/supabase-js');

module.exports = async (req, res) => {
  // Vérifier que c'est bien un appel cron de Vercel
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Configuration Supabase
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Configuration Pushover
    const PUSHOVER_API_TOKEN = process.env.PUSHOVER_API_TOKEN;
    const PUSHOVER_USER_KEY = process.env.PUSHOVER_USER_KEY;

    if (!PUSHOVER_API_TOKEN || !PUSHOVER_USER_KEY) {
      console.log('Configuration Pushover manquante');
      return res.status(500).json({ error: 'Configuration Pushover manquante' });
    }

    // Obtenir la date d'il y a 3 jours
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    const threeDaysAgoStr = threeDaysAgo.toISOString().split('T')[0];

    // Vérifier s'il y a eu des humeurs dans les 3 derniers jours
    const { data: recentMoods, error } = await supabase
      .from('moods')
      .select('*')
      .gte('date', threeDaysAgoStr);

    if (error) {
      console.error('Erreur Supabase:', error);
      return res.status(500).json({ error: 'Database error' });
    }

    // Si des humeurs ont été partagées dans les 3 derniers jours, ne pas envoyer de rappel
    if (recentMoods && recentMoods.length > 0) {
      return res.status(200).json({
        message: 'Pas de rappel nécessaire',
        reason: 'Humeurs récentes trouvées',
        recentMoodsCount: recentMoods.length,
        lastMoodDate: recentMoods[0]?.date
      });
    }

    // Envoyer rappel uniquement si aucune humeur dans les 3 derniers jours
    const reminderMessage = `🌤️ Cela fait plus de 3 jours sans nouvelles de vos météos intérieures ! 
    
N'oubliez pas de partager comment vous vous sentez aujourd'hui. 💙`;

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
            title: `Moodcast - Rappel de météo (3+ jours)`,
            device: notification.device,
            priority: 1, // Priorité haute pour rappel important
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

    const successCount = results.filter(r => r.success).length;
    
    return res.status(200).json({
      message: `Rappels envoyés (3+ jours sans humeur)`,
      sent: successCount,
      total: notifications.length,
      results: results,
      lastMoodDate: null
    });

  } catch (error) {
    console.error('Erreur dans le rappel quotidien:', error);
    return res.status(500).json({ 
      error: 'Erreur lors de l\'envoi des rappels',
      details: error.message 
    });
  }
}; 
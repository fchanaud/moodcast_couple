import { createClient } from '@supabase/supabase-js';

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
    // Configuration Supabase
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Configuration Pushover
    const PUSHOVER_API_TOKEN = process.env.PUSHOVER_API_TOKEN;
    const PUSHOVER_USER_KEY = process.env.PUSHOVER_USER_KEY;

    const { user, weather } = req.body;

    if (!user || !weather) {
      return res.status(400).json({ error: 'User and weather are required' });
    }

    // Obtenir la date d'aujourd'hui
    const today = new Date().toISOString().split('T')[0];

    // Vérifier si l'utilisateur a déjà posté aujourd'hui
    const { data: existingMood } = await supabase
      .from('moods')
      .select('*')
      .eq('user', user)
      .eq('date', today)
      .single();

    if (existingMood) {
      return res.status(400).json({ error: 'Mood already shared today' });
    }

    // Sauvegarder la nouvelle humeur
    const { data: newMood, error: insertError } = await supabase
      .from('moods')
      .insert([
        {
          user: user,
          weather: weather,
          date: today,
          created_at: new Date().toISOString()
        }
      ])
      .select()
      .single();

    if (insertError) {
      console.error('Erreur Supabase:', insertError);
      return res.status(500).json({ error: 'Database error' });
    }

    // Envoyer notification Pushover
    let notificationSent = false;
    if (PUSHOVER_API_TOKEN && PUSHOVER_USER_KEY) {
      try {
        const userName = user === 'clemence' ? 'Clémence' : 'Franklin';
        const device = user === 'clemence' ? 'iphoneF' : 'iphone';
        
        const weatherEmojis = {
          'sunny': '☀️', 'partly_sunny': '🌤️', 'cloudy': '☁️', 'overcast': '🌫️',
          'rainy': '🌧️', 'stormy': '⛈️', 'snowy': '❄️', 'windy': '💨', 'foggy': '🌁'
        };
        
        const weatherNames = {
          'sunny': 'ensoleillée', 'partly_sunny': 'avec éclaircies', 'cloudy': 'nuageuse',
          'overcast': 'couverte', 'rainy': 'pluvieuse', 'stormy': 'orageuse',
          'snowy': 'neigeuse', 'windy': 'venteuse', 'foggy': 'brumeuse'
        };

        const message = `${userName} a une météo ${weatherEmojis[weather]} ${weatherNames[weather]} aujourd'hui !`;
        
        const pushoverResponse = await fetch('https://api.pushover.net/1/messages.json', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            token: PUSHOVER_API_TOKEN,
            user: PUSHOVER_USER_KEY,
            message: message,
            title: 'Moodcast - Nouvelle météo',
            device: device
          })
        });

        notificationSent = pushoverResponse.ok;
      } catch (pushoverError) {
        console.error('Erreur Pushover:', pushoverError);
      }
    }

    return res.status(200).json({
      success: true,
      mood: newMood,
      notificationSent: notificationSent
    });

  } catch (error) {
    console.error('Erreur:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
} 
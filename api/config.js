export default function handler(req, res) {
  // Définir les headers CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  // Retourner la configuration Pushover depuis les variables d'environnement
  res.status(200).json({
    pushoverApiToken: process.env.PUSHOVER_API_TOKEN || '',
    clemenceUserKey: process.env.CLEMENCE_USER_KEY || '',
    franklinUserKey: process.env.FRANKLIN_USER_KEY || ''
  });
} 
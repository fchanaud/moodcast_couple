const { createClient } = require('@supabase/supabase-js');

module.exports = async (req, res) => {
  // Headers CORS
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

  try {
    // Configuration Supabase
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Récupérer les 10 dernières humeurs
    const { data: moods, error } = await supabase
      .from('moods')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10);

    if (error) {
      console.error('Erreur Supabase:', error);
      return res.status(500).json({ error: 'Database error' });
    }

    return res.status(200).json({
      success: true,
      moods: moods || []
    });

  } catch (error) {
    console.error('Erreur:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
}; 
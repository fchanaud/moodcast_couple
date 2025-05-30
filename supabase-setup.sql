-- Create the moods table for Moodcast
CREATE TABLE IF NOT EXISTS moods (
  id BIGSERIAL PRIMARY KEY,
  user TEXT NOT NULL CHECK (user IN ('clemence', 'franklin')),
  weather TEXT NOT NULL CHECK (weather IN ('sunny', 'partly_sunny', 'cloudy', 'overcast', 'rainy', 'stormy', 'snowy', 'windy', 'foggy')),
  date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user, date) -- Ensure only one mood per user per day
);

-- Create an index for faster queries
CREATE INDEX IF NOT EXISTS idx_moods_date ON moods(date DESC);
CREATE INDEX IF NOT EXISTS idx_moods_user_date ON moods(user, date);

-- Enable Row Level Security (RLS)
ALTER TABLE moods ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (since this is a simple shared app)
CREATE POLICY "Allow all operations on moods" ON moods
  FOR ALL USING (true); 
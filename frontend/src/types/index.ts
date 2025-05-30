export type WeatherType = 'Ensoleillé' | 'Nuageux' | 'Pluvieux' | 'Orageux' | 'Brouillard';
export type UserType = 'user1' | 'user2';

export interface EntryData {
  user: UserType;
  weather: WeatherType;
  comment?: string;
}

export interface Entry extends EntryData {
  id: string;
  timestamp: string;
} 
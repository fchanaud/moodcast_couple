import { useState, useEffect } from 'react'
import axios from 'axios'
import { Entry, EntryData, WeatherType, UserType } from './types'

const weatherOptions: WeatherType[] = ['Ensoleillé', 'Nuageux', 'Pluvieux', 'Orageux', 'Brouillard']
const userOptions: UserType[] = ['user1', 'user2']

// Icônes météo correspondantes (vous pourriez remplacer par de vraies icônes SVG)
const weatherIcons: Record<WeatherType, string> = {
  'Ensoleillé': '☀️',
  'Nuageux': '☁️',
  'Pluvieux': '🌧️',
  'Orageux': '⛈️',
  'Brouillard': '🌫️'
}

function App() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [newEntry, setNewEntry] = useState<EntryData>({
    user: 'user1',
    weather: 'Ensoleillé',
    comment: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchEntries()
  }, [])

  const fetchEntries = async () => {
    try {
      const response = await axios.get('http://localhost:8000/entries')
      setEntries(response.data)
    } catch (err) {
      console.error('Erreur lors de la récupération des entrées', err)
      setError('Impossible de charger les données')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      await axios.post('http://localhost:8000/entry', newEntry)
      
      // Réinitialiser le formulaire
      setNewEntry({
        ...newEntry,
        comment: ''
      })
      
      // Rafraîchir la liste
      fetchEntries()
    } catch (err) {
      console.error('Erreur lors de l\'envoi de l\'entrée', err)
      setError('Impossible d\'enregistrer votre météo')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setNewEntry(prev => ({ ...prev, [name]: value }))
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-6">Moodcast Couple</h1>
        
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <p className="text-center text-gray-700">
            Chaque jour, partage ta météo intérieure. Un premier pas vers une meilleure communication dans le couple.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="user">
              Qui êtes-vous ?
            </label>
            <select
              id="user"
              name="user"
              value={newEntry.user}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {userOptions.map(user => (
                <option key={user} value={user}>{user === 'user1' ? 'Utilisateur 1' : 'Utilisateur 2'}</option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="weather">
              Votre météo aujourd'hui
            </label>
            <select
              id="weather"
              name="weather"
              value={newEntry.weather}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {weatherOptions.map(weather => (
                <option key={weather} value={weather}>{weatherIcons[weather]} {weather}</option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 mb-2" htmlFor="comment">
              Un commentaire ? (facultatif)
            </label>
            <textarea
              id="comment"
              name="comment"
              value={newEntry.comment}
              onChange={handleChange}
              className="w-full p-2 border border-gray-300 rounded-md h-24"
              placeholder="Exprimez ce que vous ressentez..."
            />
          </div>

          {error && <p className="text-red-500 mb-4">{error}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
          >
            {isLoading ? 'Envoi en cours...' : 'Envoyer'}
          </button>
        </form>

        <div>
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Historique</h2>
          
          {entries.length === 0 ? (
            <p className="text-gray-500 text-center italic">Aucune entrée pour le moment</p>
          ) : (
            <ul className="space-y-4">
              {entries.map(entry => (
                <li key={entry.id} className="border-b pb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">
                        {entry.user === 'user1' ? 'Utilisateur 1' : 'Utilisateur 2'}
                      </p>
                      <p className="text-gray-500 text-sm">{formatDate(entry.timestamp)}</p>
                    </div>
                    <span className="text-2xl" title={entry.weather}>
                      {weatherIcons[entry.weather as WeatherType]}
                    </span>
                  </div>
                  {entry.comment && (
                    <p className="mt-2 text-gray-700">{entry.comment}</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

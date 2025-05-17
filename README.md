# Moodcast Couple

Application web pour partager votre météo intérieure quotidienne avec votre partenaire.

## Fonctionnalités

- Formulaire pour partager votre état émotionnel sous forme de météo
- Notifications via Pushover quand votre partenaire partage sa météo
- Rappels quotidiens à midi
- Historique des entrées

## Prérequis

- Python 3.7+
- Node.js et npm (pour le développement frontend)
- Compte Supabase (base de données PostgreSQL)
- Compte Pushover (pour les notifications)

## Configuration

1. **Cloner le dépôt**

```bash
git clone https://github.com/votrenom/moodcast_couple.git
cd moodcast_couple
```

2. **Configuration du backend**

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

3. **Configuration de Supabase**

- Créez un compte sur [Supabase](https://supabase.io/)
- Créez un nouveau projet
- Exécutez le script SQL dans `backend/sql/init.sql` dans l'éditeur SQL de Supabase

4. **Configuration des variables d'environnement**

Copiez le fichier `.env.example` en `.env` et remplissez les valeurs :

```bash
cp .env.example .env
```

Remplissez le fichier `.env` avec vos informations :

```
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_clé_supabase
PUSHOVER_API_TOKEN=votre_token_pushover
PUSHOVER_USER_1=clé_utilisateur_1
PUSHOVER_USER_2=clé_utilisateur_2
```

5. **Configuration du frontend (optional)**

Si vous avez npm installé :

```bash
cd frontend
npm install
```

## Lancement de l'application

1. **Démarrer le backend**

```bash
cd backend
uvicorn main:app --reload
```

2. **Démarrer le frontend (si vous avez npm)**

```bash
cd frontend
npm run dev
```

Ou ouvrez simplement le fichier `frontend/index.html` dans votre navigateur si vous ne pouvez pas exécuter npm.

## Déploiement sur Render

L'application est compatible avec Render pour le déploiement :

1. Backend : Service Web avec build command `pip install -r requirements.txt` et start command `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Frontend : Site statique

## Licence

MIT # moodcast_couple

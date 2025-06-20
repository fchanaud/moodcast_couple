# Moodcast Couple

Application web mobile-first pour Clémence et Franklin pour partager leur météo intérieure quotidienne.

## Fonctionnalités

- Interface mobile responsive avec sélection par icônes météo
- 9 types de météo : ☀️ 🌤️ ☁️ 🌫️ 🌧️ ⛈️ ❄️ 💨 🌁
- Une seule météo par utilisateur par jour
- Notifications Pushover avec appareils spécifiques :
  - Clémence → Notification vers iphoneF (Franklin)
  - Franklin → Notification vers iphone (Clémence)
- **Rappels quotidiens automatiques** à 17h00 (heure UK) sur les deux appareils
- Stockage local dans le navigateur (localStorage)
- Historique des météos récentes
- Bouton de test pour vérifier les rappels

## Technologies

- **Frontend** : HTML5/CSS3/JavaScript avec TailwindCSS
- **API** : Fonction serverless Vercel (Node.js)
- **Notifications** : Pushover avec ciblage d'appareils
- **Stockage** : localStorage du navigateur
- **Déploiement** : Vercel

## Configuration

### ⚠️ Configuration locale (développement)

1. **Copier le fichier d'environnement**
   ```bash
   cp .env.example .env
   ```

2. **Remplir vos vraies clés dans `.env`**
   ```bash
   PUSHOVER_API_TOKEN=votre_vrai_token_ici
   PUSHOVER_USER_KEY=votre_cle_user_partagee_ici
   ```

⚠️ **IMPORTANT** : Le fichier `.env` ne doit JAMAIS être commité sur GitHub !

### Prérequis Pushover

1. Créez un compte sur [Pushover](https://pushover.net/)
2. Créez une application pour obtenir votre **API Token**
3. Notez votre **User Key** (Clémence et Franklin partagent le même compte)
4. Configurez les appareils dans Pushover :
   - Appareil de Clémence : `iphone`
   - Appareil de Franklin : `iphoneF`

### Déploiement sur Vercel

1. **Préparer le déploiement**
   - Pushez votre code sur GitHub (le `.env` sera automatiquement ignoré)
   - Connectez votre dépôt à Vercel

2. **Configurer les variables d'environnement dans Vercel**

   Dans les paramètres Vercel, ajoutez :
   - `PUSHOVER_API_TOKEN` : Votre token d'application Pushover
   - `PUSHOVER_USER_KEY` : Votre clé utilisateur partagée
   - `CRON_SECRET` : Une clé secrète pour sécuriser les tâches cron (générez une chaîne aléatoire)

3. **Déployer**
   
   Vercel détectera automatiquement la configuration via `vercel.json`.

## Utilisation locale

1. Configurez votre fichier `.env` (voir section Configuration)
2. Ouvrez `frontend/public/index.html` dans votre navigateur
3. Les notifications Pushover fonctionneront avec vos vraies clés

## Utilisation

1. **Sélectionnez votre profil** : Clémence ou Franklin
2. **Choisissez votre météo intérieure** : Cliquez sur l'icône météo qui vous correspond
3. **Partagez** : Cliquez sur "Partager ma météo"
4. **Notification automatique** : L'autre personne reçoit une notification Pushover sur son appareil spécifique

## Types de météo disponibles

| Emoji | Météo | Description |
|-------|-------|-------------|
| ☀️ | Ensoleillé | Plein de joie et d'énergie |
| 🌤️ | Éclaircies | Plutôt bien avec quelques nuages |
| ☁️ | Nuageux | Un peu voilé mais stable |
| 🌫️ | Couvert | Ambiance feutrée et calme |
| 🌧️ | Pluvieux | Moral en baisse, besoin de réconfort |
| ⛈️ | Orageux | Tensions et émotions fortes |
| ❄️ | Neigeux | Sentiment de fraîcheur ou isolement |
| 💨 | Venteux | Agitation et changements d'humeur |
| 🌁 | Brumeux | Incertitude et confusion |

## Notifications Pushover

Le système envoie automatiquement des notifications vers l'appareil spécifique de chaque personne :

- **Quand Clémence partage** → Notification envoyée vers l'appareil `iphoneF` de Franklin
- **Quand Franklin partage** → Notification envoyée vers l'appareil `iphone` de Clémence

Format du message : "**[Prénom]** a une météo **[emoji] [description]** aujourd'hui !"

## Rappels quotidiens

Le système envoie automatiquement des rappels à **17h00 (heure UK)** tous les jours si aucune météo n'a été partagée :

- **Heure** : 17h00 UK Time (18h00 en été, 17h00 en hiver en France)
- **Destinataires** : Les deux appareils (iphone et iphoneF) reçoivent le rappel
- **Message** : Rappel amical pour encourager le partage de la météo intérieure
- **Fréquence** : Tous les jours à la même heure

### Test des rappels

Un bouton "🧪 Tester les rappels" est disponible dans l'application pour vérifier que le système fonctionne correctement.

## Notes importantes

- **Une seule météo par jour** : Impossible de changer une fois partagée
- **Stockage local** : Les données restent dans votre navigateur
- **Notifications ciblées** : Chaque utilisateur reçoit les notifications sur son appareil spécifique
- **Sécurité** : Les clés API ne sont jamais exposées dans le code source
- **Responsive** : Optimisé pour mobile et desktop

## Structure du projet

```
moodcast_couple/
├── api/
│   └── config.js            # API serverless pour Pushover
├── frontend/
│   └── public/
│       └── index.html       # Application complète (source)
├── index.html              # Application déployée (root pour Vercel)
├── package.json            # Configuration Node.js pour Vercel
├── .env.example            # Template des variables d'environnement
├── .gitignore              # Fichiers à ignorer (inclut .env)
├── vercel.json             # Configuration Vercel
└── README.md
```

## Sécurité

- ✅ `.env` est automatiquement ignoré par git
- ✅ `.env.example` fourni comme template
- ✅ Variables d'environnement séparées pour production/développement
- ✅ Aucune clé API exposée dans le code source

## Licence

MIT

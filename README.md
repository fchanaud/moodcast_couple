# Moodcast Couple

Application web mobile-first pour partager votre humeur quotidienne avec votre partenaire.

## Fonctionnalités

- Interface mobile responsive avec sélection par icônes météo
- Une seule humeur par utilisateur par jour
- Stockage local dans le navigateur (localStorage)
- Historique des humeurs récentes
- 4 types d'humeur : Très ensoleillé 🌞, Ensoleillé ☀️, Nuageux ☁️, Pluvieux 🌧️

## Technologies

- **Frontend** : HTML5/CSS3/JavaScript avec TailwindCSS
- **Stockage** : localStorage du navigateur
- **Déploiement** : Vercel (site statique)

## Prérequis

Aucun ! L'application fonctionne entièrement côté client.

## Utilisation locale

Ouvrez simplement le fichier `frontend/public/index.html` dans votre navigateur.

## Déploiement sur Vercel

1. **Préparer le déploiement**

- Pushez votre code sur GitHub
- Connectez votre dépôt à Vercel

2. **Déployer**

Vercel détectera automatiquement la configuration via `vercel.json` et servira l'application comme un site statique.

## Utilisation

1. Sélectionnez votre profil (Toi/Partenaire)
2. Cliquez sur l'icône qui représente votre humeur du jour
3. Cliquez sur "Partager mon humeur"
4. Votre humeur est sauvegardée localement
5. L'historique des humeurs récentes s'affiche en bas

**Note** : 
- Vous ne pouvez partager qu'une seule humeur par jour
- Les données sont stockées localement dans votre navigateur
- Pour partager réellement avec votre partenaire, vous devez utiliser le même appareil ou synchroniser manuellement

## Structure du projet

```
moodcast_couple/
├── frontend/
│   └── public/
│       └── index.html    # Application complète
├── vercel.json          # Configuration de déploiement
└── README.md
```

## Licence

MIT

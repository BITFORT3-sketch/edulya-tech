# Structure du projet EDULYA-TECH

```
edulya-tech/
├── index.html            → Page Accueil (header, hero, section formations, footer)
├── a-propos.html         → Page À propos (vision, mission, valeurs)
├── contact.html          → Page Contacts + formulaire
├── connexion.html        → Connexion (email, mot de passe)
├── inscription.html      → Créer un compte (nom, prénom, email, tél, mdp)
├── tableau-de-bord.html  → Espace utilisateur après connexion
├── formation-detail.html → Détail d'une formation (?id=...)
├── formation-cours.html  → Contenu du cours (protégé, réservé aux acheteurs)
├── mot-de-passe-oublie.html        → Demande de réinitialisation
├── reinitialiser-mot-de-passe.html → Choix du nouveau mot de passe
├── bienvenue.html        → Page de bienvenue avec le logo complet
├── conditions-generales.html
├── politique-confidentialite.html
├── 404.html              → Page d'erreur personnalisée
├── favicon.ico           → Icône d'onglet (généré depuis le logo)
├── css/
│   └── style.css         → Styles partagés à toutes les pages
├── js/
│   ├── config.js         → URL de l'API backend
│   └── script.js         → Interactions (menu mobile, formulaires, auth...)
├── images/
│   ├── logo-icon.png, logo-full.png
│   ├── favicon-16x16.png, favicon-32x32.png, apple-touch-icon.png
│   └── formations/       → Images des 5 formations (à déposer)
└── README.md
```

## Page 404 personnalisée

`404.html` existe mais son activation dépend de l'hébergeur :
- **GitHub Pages** : fonctionne automatiquement, rien à faire — GitHub sert
  `404.html` pour toute URL inconnue sur le site.
- **Render (Static Site)** : dans les paramètres du service, onglet
  "Redirects/Rewrites", ajoute une règle `/*` → `/404.html` avec le statut
  `404 Not Found`.

## Images à ajouter

Dépose simplement tes fichiers dans `images/formations/` avec ces noms exacts — le site les affichera automatiquement (à défaut, un dégradé de couleur s'affiche à leur place, donc rien ne casse en attendant) :

```
images/formations/
├── cyber.jpg      → carte Cybersécurité
├── web.jpg        → carte Développement Web
├── python.jpg      → carte Python
├── ia.jpg          → carte Intelligence Artificielle
└── reseaux.jpg     → carte Réseaux & Systèmes
```

Format conseillé : JPG/WebP, ~800×450px, compressées (TinyPNG ou squoosh.app) pour rester légères.

Le logo actuel est un wordmark texte (`</>` + « EDULYA-TECH ») stylé en CSS — aucun fichier requis. Si tu obtiens un vrai logo, dis-le-moi et je l'intègre à sa place.


## Backend (à ajouter séparément, en Python)

```
backend/
├── app.py                → point d'entrée (API : comptes, connexion, achats)
├── requirements.txt
├── routes/
├── models/
└── database/              → connexion Mongo / PostgreSQL selon choix final
```

## Déploiement (selon le cahier des charges)
1. Développer en local
2. Pousser le code sur GitHub
3. Connecter le dépôt GitHub à Render
4. Déployer l'app Python (backend) + le frontend
5. Obtenir l'URL publique (ex. `https://edulya-tech.onrender.com`)

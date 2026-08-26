# Backend EDULYA-TECH (Flask + PostgreSQL)

Ce backend est prêt à être déployé **directement sur Render**, sans rien installer
sur ta machine. Les tables de la base de données et le catalogue de 5 formations
sont créés **automatiquement** au premier démarrage — pas besoin de lancer une
commande manuelle.

## Déploiement sur Render (recommandé — suis ces étapes dans l'ordre)

### 1. Mettre le projet sur GitHub
Si ce n'est pas déjà fait : crée un dépôt GitHub et pousse tout le dossier
`edulya-tech/` (frontend + backend) dedans.

### 2. Créer la base de données PostgreSQL
Sur [render.com](https://render.com) (crée un compte gratuit si besoin) :
- **New +** → **PostgreSQL**
- Donne-lui un nom (ex. `edulya-tech-db`), région au choix, plan **Free**
- Une fois créée, ouvre la base et copie la valeur **Internal Database URL**
  (tu en auras besoin à l'étape suivante)

### 3. Créer le service web (le backend)
- **New +** → **Web Service**
- Connecte ton dépôt GitHub `edulya-tech`
- **Root Directory** : `backend`
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn app:app`
- **Plan** : Free

### 4. Ajouter les variables d'environnement
Dans l'onglet **Environment** du service web, ajoute :

| Clé | Valeur |
|---|---|
| `DATABASE_URL` | l'Internal Database URL copiée à l'étape 2 |
| `SECRET_KEY` | une chaîne aléatoire longue (ex. générée sur [randomkeygen.com](https://randomkeygen.com)) |
| `FRONTEND_ORIGIN` | l'URL de ton site une fois déployé (ex. `https://edulya-tech.onrender.com`) — tu peux la mettre à `*` en attendant de connaître l'URL finale |

### 5. Déployer
Clique **Create Web Service**. Render installe les dépendances, lance
`gunicorn app:app`, et au premier démarrage l'application crée toutes les
tables et insère les 5 formations automatiquement (voir `app.py`,
fonction `_seed_formations_if_needed`).

Tu obtiens une URL du type `https://edulya-tech-api.onrender.com`.
Teste-la : `https://edulya-tech-api.onrender.com/api/health` doit répondre `{"status":"ok"}`.

### 6. Connecter le frontend
Dans `js/config.js`, remplace la valeur par l'URL de ton backend Render :
```js
const API_URL = 'https://edulya-tech-api.onrender.com';
```
Puis déploie le frontend (dossier racine, sans `backend/`) comme **Static Site**
sur Render de la même façon, ou avec GitHub Pages.

---

## Sécurité : téléchargement protégé et anti brute-force

Suite à une revue de sécurité, deux protections ont été ajoutées :

- **Le lien Drive de chaque formation n'est plus jamais renvoyé dans une
  réponse API.** Le téléchargement passe uniquement par
  `GET /api/formations/<id>/telecharger`, qui vérifie côté serveur (jamais
  seulement côté frontend) que l'utilisateur est connecté **et** a bien
  acheté cette formation avant de rediriger vers le vrai fichier.
- **Anti brute-force léger** sur `/api/login` (5 essais / 15 min par email)
  et `/api/mot-de-passe-oublie` (3 demandes / 15 min par email), pour limiter
  les tentatives automatisées. Implémenté en mémoire (`rate_limit.py`), sans
  dépendance externe — suffisant pour ce projet, mais à remplacer par un
  stockage partagé (Redis) si un jour le site tourne sur plusieurs serveurs
  en parallèle.

Au démarrage, le serveur affiche aussi un avertissement dans le terminal si
`SECRET_KEY` ou `FRONTEND_ORIGIN` utilisent encore leur valeur par défaut —
pense à les changer avant un déploiement final.

## Mot de passe oublié

Un utilisateur qui a oublié son mot de passe peut cliquer sur "Mot de passe
oublié ?" à la connexion, entrer son email, et recevoir un lien (valable 1h)
pour en choisir un nouveau.

- **En local sans config email** : le lien s'affiche directement dans le
  terminal où tourne `python app.py` — copie-le dans ton navigateur pour tester.
- **Pour un vrai envoi d'email** (recommandé avant de rendre le projet) :
  configure `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` dans `.env` (ou
  dans les variables d'environnement Render). Avec Gmail : active la
  validation en 2 étapes sur le compte, puis crée un "mot de passe
  d'application" à utiliser comme `MAIL_PASSWORD` (ton vrai mot de passe
  Gmail ne fonctionnera pas directement).
- Pense aussi à définir `FRONTEND_URL` sur l'URL réelle de ton site une fois
  déployé, sinon les liens envoyés par email pointeront vers `127.0.0.1`.

## Contenu des formations (PDF)

Chaque formation a un champ `ressource_url` (lien vers un dossier Google Drive
ou un PDF) — visible uniquement par les utilisateurs qui l'ont achetée, sur le
tableau de bord et sur la page détail de la formation.

Par défaut, ce sont des liens **placeholder** (`REMPLACE_MOI_...`). Pour les
remplacer par tes vrais PDF :
1. Dépose tes PDF dans un dossier Google Drive (un dossier par formation, ou
   un lien de partage direct vers chaque PDF), et rends-le accessible via lien
2. Ouvre `seed.py`, remplace chaque `ressource_url` par ton vrai lien
3. Relance `python seed.py` (ou redéploie sur Render) pour mettre à jour la base

⚠️ **Si tu as déjà lancé le projet avant cette mise à jour**, supprime le
fichier `backend/instance/edulya_dev.db` avant de relancer `python app.py` —
ce fichier a été créé avec l'ancien schéma de base de données (sans le champ
`ressource_url`) et doit être régénéré.

## (Optionnel) Tester en local avant de déployer

Aucune installation de PostgreSQL n'est nécessaire pour tester en local : le
projet peut utiliser un fichier **SQLite** si tu définis
`DATABASE_URL=sqlite:///edulya_dev.db` dans ton `.env` local.

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

Sur Render, ce mode n'est jamais utilisé : `DATABASE_URL` y est toujours
définie (PostgreSQL), donc l'application s'y connecte directement — aucun
changement de code nécessaire.

## Qui a acheté quoi ?

La table `purchases` (modèle `Purchase` dans `models.py`) enregistre chaque
achat : elle relie l'`id` de l'utilisateur (`user_id`) à l'`id` de la formation
(`formation_id`), avec la date d'achat. Un utilisateur peut avoir plusieurs
lignes (une par formation achetée).

## Endpoints disponibles

| Méthode | Route              | Description                          | Auth requise |
|---------|---------------------|---------------------------------------|--------------|
| POST    | /api/register        | Créer un compte                       | non          |
| POST    | /api/login            | Se connecter                          | non          |
| POST    | /api/logout           | Se déconnecter                        | oui          |
| GET     | /api/me               | Infos de l'utilisateur connecté       | non (renvoie null si non connecté) |
| GET     | /api/formations       | Liste des formations                  | non          |
| GET     | /api/formations/<id>  | Détail d'une formation                | non          |
| POST    | /api/achats           | Acheter une formation (`{formation_id}`) | oui       |
| GET     | /api/mes-achats       | Mes formations achetées               | oui          |
| POST    | /api/contact           | Envoyer un message de contact         | non          |
| GET     | /api/formations/<id>/avis | Avis sur une formation achetée    | oui (achat requis) |
| POST    | /api/formations/<id>/avis | Laisser un avis sur une formation | oui (achat requis) |

L'authentification utilise une **session cookie**. Le frontend doit appeler
`fetch(url, { credentials: "include" })` pour que le cookie de session soit
envoyé/reçu correctement.

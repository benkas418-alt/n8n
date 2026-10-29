# Plan : football-intel en site web avec comptes

Statut : proposition (2026-10-29), en attente des réponses du propriétaire (section 6).

## 1. Ce qui existe déjà

- API FastAPI + tableau de bord (HTML/JS) servis par le même serveur.
- `deploy/install.sh` : installation en une commande sur un VPS Debian/Ubuntu
  (PostgreSQL, services systemd API + planificateur, premier chargement des données).
- `deploy/Caddyfile` : HTTPS automatique + un seul mot de passe pour tout le site.
- Actions d'administration protégées par un jeton unique `ADMIN_TOKEN` (D33, D43).
- Aucun compte utilisateur, aucun rôle.

## 2. Cible

| Rôle | Peut |
|---|---|
| **Super admin** (propriétaire, un seul au départ) | Tout ce que fait l'admin + nommer ou retirer des admins, voir le journal d'audit, changer les réglages sensibles (clés API, sources, modèle actif, retour arrière) |
| **Admin** | Créer, inviter, suspendre et supprimer des utilisateurs ; lancer les cycles de collecte ; voir l'administration |
| **Utilisateur** | Voir les matchs, probabilités, fiches et la fiabilité ; enregistrer ses pronostics (séparés par compte) |

## 3. Choix techniques recommandés

- **Comptes dans l'application** (pas un service externe payant) : tables `users`,
  `sessions`, `invitations`, `audit_log` dans PostgreSQL (migration Alembic).
- Mots de passe hachés avec **Argon2** (`argon2-cffi`) ; jamais stockés en clair.
- **Sessions côté serveur** : cookie `HttpOnly`, `Secure`, `SameSite=Lax`, expiration
  14 jours ; protection CSRF sur les actions qui modifient des données.
- **Inscription sur invitation** (lien à usage unique, valable 7 jours) plutôt
  qu'inscription libre : contrôle de qui voit les données (voir section 5).
- Limitation des tentatives de connexion (anti force brute).
- Super admin créé en ligne de commande sur le serveur
  (`footintel users create-superadmin`), jamais depuis le site.
- Double authentification (TOTP) pour super admin et admins : phase 2.
- Mot de passe oublié : par lien e-mail si un service d'envoi est configuré
  (Resend, Brevo… à choisir) ; sinon réinitialisation par un admin.
- Le mot de passe Caddy global est retiré une fois les comptes en place.
- Les pronostics actuels (table des choix) passent sous l'identifiant de l'utilisateur.

## 4. Hébergement

- VPS (2 vCPU, 4 Go RAM ; environ 4 à 8 €/mois, prix à vérifier) + nom de domaine.
- `deploy/install.sh` existant, puis migration des comptes, puis Caddyfile sans
  `basic_auth`.
- Sauvegarde quotidienne de PostgreSQL hors du serveur.

## 5. Point juridique à trancher avant d'ouvrir des comptes

- **OneFootball** (D50) et **Sofascore** (D56) sont utilisés « pour usage personnel,
  rien de publié ». Un site avec des comptes pour d'autres personnes **publie** ces
  données. Options : masquer aux utilisateurs tout ce qui vient de ces sources
  (compositions, formations, onglet Joueurs, profils tactiques), ou accepter le risque
  par une nouvelle décision explicite.
- **The Odds API** et **football-data.org** : vérifier que leur offre gratuite autorise
  l'affichage à des tiers (attribution déjà en pied de page).
- Si le site devient payant ou présenté comme conseil de paris : conditions bien plus
  strictes (jeux d'argent, protection des consommateurs) ; à vérifier pour la RDC et
  les pays des utilisateurs.

## 6. Questions au propriétaire

1. Qui aura un compte : quelques proches, un public large, des clients payants ?
2. Inscription libre ou sur invitation ?
3. Que faire des données OneFootball/Sofascore pour les autres utilisateurs (section 5) ?
4. Un VPS et un nom de domaine sont-ils disponibles ?

## 7. Étapes une fois les réponses connues

1. Modèle de données + migration + commandes CLI (super admin, utilisateurs).
2. Connexion/déconnexion, sessions, invitations, rôles sur chaque route de l'API.
3. Pages : connexion, invitation, gestion des utilisateurs (admin), gestion des admins
   et journal (super admin).
4. Tests : droits par rôle (un utilisateur ne peut pas appeler une route admin, etc.).
5. Déploiement sur le VPS, puis retrait du mot de passe Caddy global.

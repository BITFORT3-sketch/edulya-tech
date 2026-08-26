"""
Limiteur de tentatives très simple, en mémoire — sans dépendance externe.

Protège /api/login et /api/mot-de-passe-oublie contre les tentatives
répétées (brute-force / spam d'emails de réinitialisation).

LIMITE CONNUE : ce compteur vit en mémoire du processus. Avec un seul
worker (comme en local, ou un plan gratuit Render à une seule instance),
c'est suffisant. Avec plusieurs workers/instances en production, chacun
aurait son propre compteur — il faudrait alors un stockage partagé
(ex: Redis) pour une vraie limite globale. Largement suffisant pour ce
projet.
"""

import time
from collections import defaultdict

_tentatives = defaultdict(list)


def trop_de_tentatives(cle, max_tentatives=5, fenetre_secondes=15 * 60):
    """Retourne True si `cle` (ex: email ou IP) a dépassé la limite récemment."""
    maintenant = time.time()
    _tentatives[cle] = [t for t in _tentatives[cle] if maintenant - t < fenetre_secondes]
    return len(_tentatives[cle]) >= max_tentatives


def enregistrer_tentative(cle):
    _tentatives[cle].append(time.time())


def reinitialiser_tentatives(cle):
    _tentatives[cle] = []

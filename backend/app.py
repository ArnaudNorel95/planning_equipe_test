"""
Test technique — Planning Équipe
================================
Application aiohttp avec 3 endpoints à implémenter.

Les données sont chargées depuis les fichiers JSON du dossier data/ :
  - calendrier.json : calendrier de la saison (journées et grille de rencontres)
  - equipes.json    : équipes, leur numéro de grille et leur terrain domicile
  - terrains.json   : terrains et leurs occupations (événements tiers)

Elles sont accessibles dans chaque handler via request.app["calendrier"], etc.

Concepts clés
-------------
- **Numéro de grille** : chaque équipe a un numéro (1‥N). La grille du
  calendrier définit, pour chaque journée, quels numéros jouent à domicile
  et lesquels jouent à l'extérieur.
- **Swap** : changer le numéro de grille d'une équipe revient à l'échanger
  avec l'équipe qui détenait le numéro cible.
- **Conflit d'installation** : un match est en conflit si, sur le même
  terrain et la même date, une occupation tierce chevauche le créneau du
  match.  Chevauchement = match_debut < occupation_fin ET occupation_debut < match_fin.
  Durée d'un match = calendrier["duree_match_minutes"].
"""
from aiohttp import web
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


@web.middleware
async def cors_middleware(request, handler):
    """Middleware CORS pour permettre les requêtes depuis le frontend."""
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        try:
            response = await handler(request)
        except web.HTTPException as exc:
            response = exc
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ---------------------------------------------------------------------------
# ENDPOINT 1 — GET /api/planning/{club_id}
# ---------------------------------------------------------------------------
async def get_planning(request):
    """
    Retourne le planning complet d'un club pour la saison.

    Pour chaque semaine (de semaine_debut à semaine_debut − 1, soit 52 semaines),
    retourne le match du club s'il y en a un, avec les éventuels conflits
    d'installation détectés.

    Réponse attendue (200) :
    {
        "club_id": "PSG",
        "club_nom": "Paris Saint-Germain",
        "numero_grille": 1,
        "numeros_grilles_disponibles": [2, 3, 4],
        "semaines": [
            {"numero": 27, "match": null},
            ...
            {
                "numero": 35,
                "match": {
                    "journee": 1,
                    "date": "2025-08-30",
                    "heure": "21:00",
                    "adversaire": "LOSC Lille",
                    "domicile": true,
                    "terrain_nom": "Parc des Princes",
                    "conflits": []
                }
            },
            ...
        ]
    }

    Erreurs :
      404 — club_id inconnu
    """
    # TODO: À implémenter
    raise NotImplementedError("GET /api/planning/{club_id}")


# ---------------------------------------------------------------------------
# ENDPOINT 2 — POST /api/planning/{club_id}/conflicts
# ---------------------------------------------------------------------------
async def preview_conflicts(request):
    """
    Prévisualisation : recalcule le planning avec un nouveau numéro de grille
    SANS persister le changement.

    Le changement de grille implique un swap : l'équipe qui possédait le
    numéro cible reçoit l'ancien numéro du club, et le club reçoit le nouveau.
    Ce swap ne doit PAS être sauvegardé dans request.app["equipes"].

    Corps de la requête :
    {
        "nouveau_numero_grille": 3
    }

    Réponse (200) : même format que GET, avec le nouveau numéro appliqué.

    Erreurs :
      404 — club_id inconnu
      400 — nouveau_numero_grille absent, hors limites (1..nb_equipes),
            ou identique au numéro actuel
    """
    # TODO: À implémenter
    raise NotImplementedError("POST /api/planning/{club_id}/conflicts")


# ---------------------------------------------------------------------------
# ENDPOINT 3 — PUT /api/planning/{club_id}/grille
# ---------------------------------------------------------------------------
async def update_grille(request):
    """
    Met à jour le numéro de grille du club (swap) et retourne le planning
    avec les conflits recalculés.

    Le changement est PERSISTÉ : mise à jour en mémoire (request.app["equipes"])
    ET écriture dans le fichier data/equipes.json.

    Corps de la requête :
    {
        "nouveau_numero_grille": 3
    }

    Réponse (200) : même format que GET.

    Erreurs :
      404 — club_id inconnu
      400 — nouveau_numero_grille absent, hors limites, ou identique au numéro actuel
    """
    # TODO: À implémenter
    raise NotImplementedError("PUT /api/planning/{club_id}/grille")


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
def create_app():
    """Crée et configure l'application aiohttp."""
    app = web.Application(middlewares=[cors_middleware])

    # Chargement des données
    app["calendrier"] = load_json("calendrier.json")
    app["equipes"] = load_json("equipes.json")
    app["terrains"] = load_json("terrains.json")

    # Routes
    app.router.add_get("/api/planning/{club_id}", get_planning)
    app.router.add_post("/api/planning/{club_id}/conflicts", preview_conflicts)
    app.router.add_put("/api/planning/{club_id}/grille", update_grille)

    return app


if __name__ == "__main__":
    web.run_app(create_app(), port=8080)

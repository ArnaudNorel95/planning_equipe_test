# Test technique — Planning Équipe

## Contexte

Tu travailles sur un outil de gestion de compétitions de football.
L'application affiche le **planning d'une équipe** sur une saison entière
(semaine 27 à semaine 26 de l'année suivante) et détecte les **conflits
d'installation** (deux événements qui se chevauchent sur le même terrain).

Chaque équipe possède un **numéro de grille** qui détermine son calendrier
domicile/extérieur. Changer ce numéro modifie les matchs (adversaires,
terrains) et peut créer ou supprimer des conflits.

## Ce qui est fourni

| Fichier | Rôle |
|---------|------|
| `frontend/index.html` | Interface minimale (ouvrir dans un navigateur) |
| `backend/app.py` | Application aiohttp avec 3 endpoints **à implémenter** |
| `backend/data/calendrier.json` | Calendrier : journées, dates et grille de rencontres |
| `backend/data/equipes.json` | Équipes, numéro de grille et terrain domicile |
| `backend/data/terrains.json` | Terrains et occupations tierces |
| `backend/tests/` | Suite de tests (30 tests) |

## Pré-requis

- **Python 3.8+** (testé jusqu'à 3.12)

## Installation

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Lancer les tests

```bash
cd backend
pytest -v
```

Tous les tests échouent au départ (`NotImplementedError`). L'objectif est de
les faire passer.

## Lancer le serveur

```bash
cd backend
python app.py          # écoute sur http://localhost:8080
```

Puis ouvrir `frontend/index.html` dans un navigateur.

---

## Les 3 endpoints à implémenter

### 1. `GET /api/planning/{club_id}`

Retourne le planning complet du club pour la saison.

- 52 semaines (S27 → S52, puis S1 → S26)
- Pour chaque semaine : `null` si pas de match, sinon les infos du match
- Détecter les conflits d'installation

### 2. `POST /api/planning/{club_id}/conflicts`

**Prévisualisation** : applique un nouveau numéro de grille et retourne le
planning recalculé **sans sauvegarder** le changement.

- Body : `{"nouveau_numero_grille": 3}`
- Le swap (échange de numéro avec l'équipe cible) ne doit pas être persisté

### 3. `PUT /api/planning/{club_id}/grille`

Met à jour le numéro de grille (swap persisté) et retourne le planning.

- Body : `{"nouveau_numero_grille": 3}`
- Le changement est sauvegardé dans `request.app["equipes"]`

---

## Modèle de données

### Calendrier (`calendrier.json`)

```
journees[].rencontres[] = { "dom": <n° grille domicile>, "ext": <n° grille extérieur> }
```

Le numéro de grille d'une équipe détermine dans quelle rencontre elle joue
et si elle est à domicile ou à l'extérieur.

### Équipes (`equipes.json`)

Chaque équipe a un `terrain_id`. Quand une équipe joue **à domicile**, le
match se joue sur **son** terrain. Quand elle joue **à l'extérieur**, c'est
sur le terrain de l'adversaire.

### Terrains (`terrains.json`)

Les occupations représentent des événements tiers déjà programmés sur le
terrain (matchs d'autres compétitions, concerts, etc.).

### Conflit d'installation

Un match est en conflit si, sur le **même terrain** et la **même date**, une
occupation tierce **chevauche** le créneau du match.

```
Chevauchement = match_debut < occupation_fin  ET  occupation_debut < match_fin
Durée match  = calendrier.duree_match_minutes (en minutes)
```

Le conflit est marqué `"installation"` dans la liste `conflits` du match.

---

## Format de réponse attendu

```json
{
  "club_id": "PSG",
  "club_nom": "Paris Saint-Germain",
  "numero_grille": 1,
  "numeros_grilles_disponibles": [2, 3, 4],
  "semaines": [
    { "numero": 27, "match": null },
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
    }
  ]
}
```

## Codes d'erreur

| Code | Cas |
|------|-----|
| 404 | `club_id` inconnu |
| 400 | `nouveau_numero_grille` absent, hors limites (1..nb_equipes), ou identique au numéro actuel |

"""Tests pour GET /api/planning/{club_id}"""


class TestGetPlanning:

    async def test_returns_200(self, client):
        resp = await client.get("/api/planning/PSG")
        assert resp.status == 200

    async def test_response_structure(self, client):
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert data["club_id"] == "PSG"
        assert data["club_nom"] == "Paris Saint-Germain"
        assert data["numero_grille"] == 1
        assert "numeros_grilles_disponibles" in data
        assert "semaines" in data

    async def test_52_weeks(self, client):
        """Le planning contient exactement 52 semaines."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert len(data["semaines"]) == 52

    async def test_weeks_order(self, client):
        """Les semaines vont de S27 à S26 (saison sportive juillet → juin)."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        week_numbers = [s["numero"] for s in data["semaines"]]
        expected = list(range(27, 53)) + list(range(1, 27))
        assert week_numbers == expected

    async def test_has_6_matches(self, client):
        """PSG a 6 matchs dans la saison (4 équipes, 6 journées)."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        matches = [s for s in data["semaines"] if s["match"] is not None]
        assert len(matches) == 6

    async def test_match_fields(self, client):
        """Chaque match doit contenir tous les champs attendus."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        required_fields = {"journee", "date", "heure", "adversaire",
                           "domicile", "terrain_nom", "conflits"}
        for s in data["semaines"]:
            if s["match"] is not None:
                assert required_fields.issubset(s["match"].keys()), \
                    f"Champs manquants semaine {s['numero']}"

    async def test_no_conflicts_with_grille_1(self, client):
        """Avec la grille 1, aucun match du PSG n'a de conflit."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        for s in data["semaines"]:
            if s["match"]:
                assert s["match"]["conflits"] == [], \
                    f"Conflit inattendu S{s['numero']}: {s['match']['conflits']}"

    async def test_correct_opponents_grille_1(self, client):
        """Vérifie adversaires et dom/ext pour chaque journée avec la grille 1."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        by_j = {s["match"]["journee"]: s["match"]
                for s in data["semaines"] if s["match"]}

        assert by_j[1]["adversaire"] == "LOSC Lille"
        assert by_j[1]["domicile"] is True
        assert by_j[2]["adversaire"] == "Olympique Lyonnais"
        assert by_j[2]["domicile"] is False
        assert by_j[3]["adversaire"] == "Olympique de Marseille"
        assert by_j[3]["domicile"] is True
        assert by_j[4]["adversaire"] == "LOSC Lille"
        assert by_j[4]["domicile"] is False
        assert by_j[5]["adversaire"] == "Olympique Lyonnais"
        assert by_j[5]["domicile"] is True
        assert by_j[6]["adversaire"] == "Olympique de Marseille"
        assert by_j[6]["domicile"] is False

    async def test_correct_terrains_grille_1(self, client):
        """Matchs à domicile au Parc des Princes, extérieur chez l'adversaire."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        by_j = {s["match"]["journee"]: s["match"]
                for s in data["semaines"] if s["match"]}

        assert by_j[1]["terrain_nom"] == "Parc des Princes"       # dom
        assert by_j[2]["terrain_nom"] == "Groupama Stadium"        # ext → OL
        assert by_j[3]["terrain_nom"] == "Parc des Princes"        # dom
        assert by_j[4]["terrain_nom"] == "Stade Pierre-Mauroy"    # ext → LOSC
        assert by_j[5]["terrain_nom"] == "Parc des Princes"        # dom
        assert by_j[6]["terrain_nom"] == "Stade Vélodrome"         # ext → OM

    async def test_available_grilles(self, client):
        """Les grilles disponibles sont toutes sauf celle du club."""
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert sorted(data["numeros_grilles_disponibles"]) == [2, 3, 4]

    async def test_unknown_club_returns_404(self, client):
        resp = await client.get("/api/planning/TOTO")
        assert resp.status == 404

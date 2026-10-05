"""Tests pour POST /api/planning/{club_id}/conflicts (prévisualisation)."""


class TestPreview:

    async def test_returns_200(self, client):
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        assert resp.status == 200

    async def test_shows_new_grille(self, client):
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        assert data["numero_grille"] == 3

    async def test_has_2_conflicts_with_grille_3(self, client):
        """Grille 3 → PSG joue à domicile S38 et S7, deux occupations chevauchent."""
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        conflicts = [s for s in data["semaines"]
                     if s["match"] and s["match"]["conflits"]]
        assert len(conflicts) == 2

    async def test_conflict_on_correct_weeks(self, client):
        """Les conflits tombent sur les semaines 38 et 7."""
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        conflict_weeks = sorted(
            s["numero"] for s in data["semaines"]
            if s["match"] and s["match"]["conflits"]
        )
        assert conflict_weeks == sorted([38, 7])

    async def test_conflict_marker_is_installation(self, client):
        """Le type de conflit doit être 'installation'."""
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        for s in data["semaines"]:
            if s["match"] and s["match"]["conflits"]:
                assert "installation" in s["match"]["conflits"]

    async def test_does_not_persist(self, client):
        """Après une prévisualisation, le GET doit toujours retourner la grille initiale."""
        await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert data["numero_grille"] == 1

    async def test_correct_opponents_grille_3(self, client):
        """Avec la grille 3, les adversaires et dom/ext changent."""
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        by_j = {s["match"]["journee"]: s["match"]
                for s in data["semaines"] if s["match"]}

        # J1 : OM(dom) vs PSG(ext)
        assert by_j[1]["adversaire"] == "Olympique de Marseille"
        assert by_j[1]["domicile"] is False
        # J2 : PSG(dom) vs OL(ext)
        assert by_j[2]["adversaire"] == "Olympique Lyonnais"
        assert by_j[2]["domicile"] is True
        # J3 : PSG(dom) vs LOSC(ext)
        assert by_j[3]["adversaire"] == "LOSC Lille"
        assert by_j[3]["domicile"] is True

    async def test_no_conflict_with_grille_2(self, client):
        """Grille 2 → pas de conflit (aucune occupation ne chevauche)."""
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 2},
        )
        data = await resp.json()
        conflicts = [s for s in data["semaines"]
                     if s["match"] and s["match"]["conflits"]]
        assert len(conflicts) == 0

    async def test_invalid_grille_too_high(self, client):
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 99},
        )
        assert resp.status == 400

    async def test_invalid_grille_zero(self, client):
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 0},
        )
        assert resp.status == 400

    async def test_same_grille_returns_400(self, client):
        resp = await client.post(
            "/api/planning/PSG/conflicts",
            json={"nouveau_numero_grille": 1},
        )
        assert resp.status == 400

    async def test_missing_body_returns_400(self, client):
        resp = await client.post("/api/planning/PSG/conflicts", json={})
        assert resp.status == 400

    async def test_unknown_club_returns_404(self, client):
        resp = await client.post(
            "/api/planning/TOTO/conflicts",
            json={"nouveau_numero_grille": 2},
        )
        assert resp.status == 404

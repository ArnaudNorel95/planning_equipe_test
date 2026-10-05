"""Tests pour PUT /api/planning/{club_id}/grille (mise à jour persistée)."""


class TestUpdateGrille:

    async def test_returns_200(self, client):
        resp = await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        assert resp.status == 200

    async def test_persists_new_grille(self, client):
        """Après un PUT, le GET doit retourner le nouveau numéro."""
        await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert data["numero_grille"] == 3

    async def test_has_2_conflicts_with_grille_3(self, client):
        resp = await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        data = await resp.json()
        conflicts = [s for s in data["semaines"]
                     if s["match"] and s["match"]["conflits"]]
        assert len(conflicts) == 2

    async def test_swap_is_coherent(self, client):
        """Après PSG → grille 3, OL doit avoir récupéré la grille 1."""
        await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        resp = await client.get("/api/planning/OL")
        data = await resp.json()
        assert data["numero_grille"] == 1

    async def test_revert_removes_conflicts(self, client):
        """Grille 3 puis retour en grille 1 → 0 conflit."""
        await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 1},
        )
        resp = await client.get("/api/planning/PSG")
        data = await resp.json()
        assert data["numero_grille"] == 1
        for s in data["semaines"]:
            if s["match"]:
                assert s["match"]["conflits"] == []

    async def test_persists_to_file(self, client, equipes_file):
        """Le PUT doit écrire les modifications dans data/equipes.json."""
        await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 3},
        )
        import json
        with open(equipes_file) as f:
            equipes = json.load(f)
        psg = next(e for e in equipes if e["id"] == "PSG")
        assert psg["numero_grille"] == 3

    async def test_invalid_grille(self, client):
        resp = await client.put(
            "/api/planning/PSG/grille",
            json={"nouveau_numero_grille": 0},
        )
        assert resp.status == 400

    async def test_unknown_club(self, client):
        resp = await client.put(
            "/api/planning/TOTO/grille",
            json={"nouveau_numero_grille": 2},
        )
        assert resp.status == 404

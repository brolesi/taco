"""Testes do gerador da API estática (GitHub Pages)."""

import json

from api.main import API_VERSION, get_food
from scripts.build_static_api import _slug, construir


def test_slug():
    assert _slug("Bebidas (alcoólicas e não alcoólicas)") == "bebidas-alcoolicas-e-nao-alcoolicas"
    assert _slug("Cereais e derivados") == "cereais-e-derivados"


def test_site_estatico_reflete_a_api(tmp_path):
    total = construir(tmp_path)
    assert total > 2000

    # O JSON estático tem de ser idêntico ao que a API dinâmica devolve: as
    # duas saem da mesma função, e este teste é o que garante que continuem.
    estatico = json.loads((tmp_path / "foods" / "561.json").read_text(encoding="utf-8"))
    assert estatico == json.loads(json.dumps(get_food(561)))
    assert estatico["description"] == "Feijão, carioca, cozido"

    indice = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    assert indice["version"] == API_VERSION
    assert indice["total_foods"] == 597

    medidas = json.loads((tmp_path / "measures" / "index.json").read_text(encoding="utf-8"))
    assert medidas["total"] == 1119

    # NaN não é JSON válido; nutriente ausente tem de virar null.
    bruto = (tmp_path / "foods" / "1.json").read_text(encoding="utf-8")
    assert "NaN" not in bruto
    assert json.loads(bruto)["cholesterol_mg"] is None

    # Sem isto o GitHub Pages roda Jekyll e some com diretórios "_".
    assert (tmp_path / ".nojekyll").is_file()
    assert (tmp_path / "index.html").is_file()

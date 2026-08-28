"""Testes da API TACO usando o TestClient do FastAPI."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "TACO Nutritional Data API"
    assert body["total_foods"] > 0


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_categories():
    resp = client.get("/categories")
    assert resp.status_code == 200
    categories = resp.json()
    assert len(categories) == 15
    assert all("category" in c and "food_count" in c for c in categories)


def test_get_category():
    resp = client.get("/categories/Cereais e derivados")
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "Cereais e derivados"
    assert body["food_count"] > 0


def test_categories_derived_from_sheet_separators():
    # Regressão: as categorias vêm das linhas separadoras da planilha, não de
    # faixas numéricas (o feijão carioca já foi rotulado "Produtos açucarados").
    resp = client.get("/foods/561")
    assert resp.status_code == 200
    body = resp.json()
    assert "feijão" in body["description"].lower()
    assert body["category"] == "Leguminosas e derivados"


def test_get_category_not_found():
    resp = client.get("/categories/inexistente")
    assert resp.status_code == 404


def test_list_foods_pagination():
    resp = client.get("/foods", params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["foods"]) == 5
    assert body["total"] >= 500


def test_list_foods_search():
    resp = client.get("/foods", params={"search": "arroz"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    assert all("arroz" in f["description"].lower() for f in body["foods"])


def test_list_foods_search_regex_chars_are_literal():
    # Caracteres especiais de regex não devem quebrar a busca.
    resp = client.get("/foods", params={"search": "(arroz"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_foods_search_ignora_acentos():
    # "acucar" deve encontrar "açúcar".
    sem_acento = client.get("/foods", params={"search": "acucar", "limit": 100}).json()
    com_acento = client.get("/foods", params={"search": "açúcar", "limit": 100}).json()
    assert sem_acento["total"] > 0
    assert [f["id"] for f in sem_acento["foods"]] == [f["id"] for f in com_acento["foods"]]


def test_get_food():
    resp = client.get("/foods/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert "arroz" in body["description"].lower()
    assert body["category"] == "Cereais e derivados"
    assert isinstance(body["energy_kcal"], (int, float))


def test_get_food_not_found():
    resp = client.get("/foods/99999")
    assert resp.status_code == 404


def test_get_food_fatty_acids():
    resp = client.get("/foods/1/fatty-acids")
    assert resp.status_code == 200
    assert "saturated_g" in resp.json()


def test_get_food_amino_acids_not_available():
    # O alimento 1 existe, mas não consta na tabela de aminoácidos.
    resp = client.get("/foods/1/amino-acids")
    assert resp.status_code == 404


def test_compare_foods():
    resp = client.post("/foods/compare", json={"ids": [1, 2]})
    assert resp.status_code == 200
    body = resp.json()
    assert [f["id"] for f in body] == [1, 2]


def test_compare_requires_two_ids():
    resp = client.post("/foods/compare", json={"ids": [1]})
    assert resp.status_code == 422


def test_sum_nutrients():
    resp = client.post(
        "/foods/sum",
        json={"items": [{"id": 1, "grams": 100}, {"id": 2, "grams": 50}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["total_nutrients"]["energy_kcal"] > 0


def test_sum_rejects_empty_items():
    resp = client.post("/foods/sum", json={"items": []})
    assert resp.status_code == 422


def test_sum_rejects_non_positive_grams():
    resp = client.post("/foods/sum", json={"items": [{"id": 1, "grams": 0}]})
    assert resp.status_code == 422


def test_sum_reporta_nutrientes_sem_dado():
    # O alimento 1 não tem valor de vitamina C na TACO: o total não deve
    # contá-lo como zero sem avisar.
    body = client.post("/foods/sum", json={"items": [{"id": 1, "grams": 100}]}).json()
    assert body["missing_values"]["vitamin_c_mg"] == 1
    assert "energy_kcal" not in body["missing_values"]

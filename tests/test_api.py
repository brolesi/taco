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


def test_facetas_no_alimento():
    body = client.get("/foods/1").json()
    assert body["base_name"] == "Arroz"
    assert body["preparation"] == "cozido"
    assert body["qualifiers"] == "integral"


def test_list_preparations():
    preparos = {p["preparation"]: p["food_count"] for p in client.get("/preparations").json()}
    assert preparos["cru"] > preparos["cozido"] > 0
    assert None not in preparos  # alimentos sem preparo ficam fora da contagem


def test_filtro_por_base_e_preparo():
    body = client.get("/foods", params={"base_name": "arroz", "preparation": "cozido"}).json()
    assert body["total"] > 0
    assert all("cozido" in f["description"].lower() for f in body["foods"])
    assert all(f["description"].lower().startswith("arroz") for f in body["foods"])


def test_filtro_por_base_ignora_acentos():
    com = client.get("/foods", params={"base_name": "feijão"}).json()["total"]
    sem = client.get("/foods", params={"base_name": "feijao"}).json()["total"]
    assert com == sem > 0


def test_facetas_nao_entram_na_soma():
    totais = client.post("/foods/sum", json={"items": [{"id": 1, "grams": 100}]}).json()
    assert "base_name" not in totais["total_nutrients"]
    assert "preparation" not in totais["total_nutrients"]


def test_health_reporta_medidas():
    assert client.get("/health").json()["total_measures"] == 11801


def test_list_measures_busca_e_filtro():
    body = client.get("/measures", params={"search": "arroz", "measure": "colher de sopa"}).json()
    assert body["total"] > 0
    assert all("ARROZ" in m["food_description"] for m in body["measures"])
    assert all(m["measure"] == "COLHER DE SOPA" for m in body["measures"])
    assert all(m["grams"] > 0 for m in body["measures"])


def test_list_measures_ignora_acentos():
    com = client.get("/measures", params={"search": "feijão"}).json()["total"]
    sem = client.get("/measures", params={"search": "feijao"}).json()["total"]
    assert com == sem > 0


def test_list_measures_paginacao():
    body = client.get("/measures", params={"limit": 5, "skip": 10}).json()
    assert len(body["measures"]) == 5
    assert body["total"] == 11801


def test_list_measure_types():
    tipos = client.get("/measures/types").json()
    assert {"measure": "COLHER DE SOPA", "record_count": 578} in tipos


def test_variants_agrupa_por_base_e_qualificadores():
    body = client.get("/foods/273/variants").json()  # Abadejo, filé, congelado, assado
    assert body["base_name"] == "Abadejo"
    preparos = {v["preparation"] for v in body["variants"]}
    assert preparos == {"cozido", "cru", "grelhado"}
    assert 273 not in [v["id"] for v in body["variants"]]  # não devolve a si mesmo
    # Umidade acompanha cada variante: é o que separa diferença de água de
    # perda de nutriente.
    assert all(v["moisture_pct"] > 0 for v in body["variants"])


def test_variants_nao_mistura_qualificadores_diferentes():
    # "Arroz, integral, cozido" pareia com "Arroz, integral, cru", nunca com
    # "Arroz, tipo 1, cru".
    body = client.get("/foods/1/variants").json()
    assert [v["description"] for v in body["variants"]] == ["Arroz, integral, cru"]


def test_variants_de_alimento_inexistente():
    assert client.get("/foods/99999/variants").status_code == 404


def test_coverage_lista_pior_cobertura_primeiro():
    body = client.get("/coverage").json()
    assert body["total_foods"] == 597
    pcts = [c["coverage_pct"] for c in body["composition"]]
    assert pcts == sorted(pcts)
    por_campo = {c["field"]: c for c in body["composition"]}
    # Metade da TACO não tem vitamina A; quase tudo tem energia.
    assert por_campo["rae_mcg"]["coverage_pct"] < 50
    assert por_campo["energy_kcal"]["coverage_pct"] > 98
    assert por_campo["rae_mcg"]["with_data"] < por_campo["energy_kcal"]["with_data"]
    assert body["tables"]["amino_acids"]["foods"] == 26


def test_cors_liberado_para_front_end():
    # Dados públicos e somente-leitura: qualquer origem pode consumir.
    resp = client.get("/foods/1", headers={"Origin": "https://exemplo.com"})
    assert resp.headers["access-control-allow-origin"] == "*"
    preflight = client.options(
        "/foods/sum",
        headers={"Origin": "https://exemplo.com", "Access-Control-Request-Method": "POST"},
    )
    assert preflight.status_code == 200
    assert "POST" in preflight.headers["access-control-allow-methods"]

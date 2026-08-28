"""API REST para a Tabela Brasileira de Composição de Alimentos (TACO).

Serve os CSVs canônicos gerados por ``scripts/process_taco.py`` a partir da
planilha original da TACO (4ª edição, NEPA/UNICAMP). As colunas em português
(snake_case) dos CSVs são expostas com nomes de campo em inglês, mantendo o
contrato público da API.
"""

from __future__ import annotations

import math
import unicodedata
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, create_model

API_VERSION = "1.3.0"

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "taco"

# Casas decimais nas respostas. Cinco casas preservam o valor-traço (1e-5)
# e eliminam ruído de ponto flutuante dos valores médios do pipeline.
DECIMAL_PLACES = 5

# ---------------------------------------------------------------------------
# Mapeamento de colunas: CSV (pt-BR snake_case) -> campo da API (en)
# ---------------------------------------------------------------------------

COMPOSITION_COLUMNS = {
    "numero_alimento": "id",
    "categoria": "category",
    "descricao": "description",
    "base": "base_name",
    "preparo": "preparation",
    "qualificadores": "qualifiers",
    "umidade_pct": "moisture_pct",
    "energia_kcal": "energy_kcal",
    "energia_kj": "energy_kj",
    "proteina_g": "protein_g",
    "lipideos_g": "lipids_g",
    "colesterol_mg": "cholesterol_mg",
    "carboidrato_g": "carbohydrate_g",
    "fibra_g": "dietary_fiber_g",
    "cinzas_g": "ash_g",
    "calcio_mg": "calcium_mg",
    "magnesio_mg": "magnesium_mg",
    "manganes_mg": "manganese_mg",
    "fosforo_mg": "phosphorus_mg",
    "ferro_mg": "iron_mg",
    "sodio_mg": "sodium_mg",
    "potassio_mg": "potassium_mg",
    "cobre_mg": "copper_mg",
    "zinco_mg": "zinc_mg",
    "retinol_mcg": "retinol_mcg",
    "RE_mcg": "re_mcg",
    "RAE_mcg": "rae_mcg",
    "tiamina_mg": "thiamine_mg",
    "riboflavina_mg": "riboflavin_mg",
    "piridoxina_mg": "pyridoxine_mg",
    "niacina_mg": "niacin_mg",
    "vitamina_c_mg": "vitamin_c_mg",
}

FATTY_ACIDS_COLUMNS = {
    "numero_alimento": "id",
    "categoria": "category",
    "descricao": "description",
    "saturados_g": "saturated_g",
    "monoinsaturados_g": "monounsaturated_g",
    "poliinsaturados_g": "polyunsaturated_g",
    "c12_0_g": "c12_0_g",
    "c14_0_g": "c14_0_g",
    "c16_0_g": "c16_0_g",
    "c18_0_g": "c18_0_g",
    "c20_0_g": "c20_0_g",
    "c22_0_g": "c22_0_g",
    "c24_0_g": "c24_0_g",
    "c14_1_g": "c14_1_g",
    "c16_1_g": "c16_1_g",
    "c18_1_g": "c18_1_g",
    "c20_1_g": "c20_1_g",
    "c18_2n6_g": "c18_2_n6_g",
    "c18_3n3_g": "c18_3_n3_g",
    "c20_4_g": "c20_4_g",
    "c20_5_g": "epa_c20_5_g",
    "c22_5_g": "dpa_c22_5_g",
    "c22_6_g": "dha_c22_6_g",
    "c18_1t_g": "trans_c18_1_g",
    "c18_2t_g": "trans_c18_2_g",
}

AMINO_ACIDS_COLUMNS = {
    "numero_alimento": "id",
    "categoria": "category",
    "descricao": "description",
    "triptofano_g": "tryptophan_g",
    "treonina_g": "threonine_g",
    "isoleucina_g": "isoleucine_g",
    "leucina_g": "leucine_g",
    "lisina_g": "lysine_g",
    "metionina_g": "methionine_g",
    "cistina_g": "cystine_g",
    "fenilalanina_g": "phenylalanine_g",
    "tirosina_g": "tyrosine_g",
    "valina_g": "valine_g",
    "arginina_g": "arginine_g",
    "histidina_g": "histidine_g",
    "alanina_g": "alanine_g",
    "acido_aspartico_g": "aspartic_acid_g",
    "acido_glutamico_g": "glutamic_acid_g",
    "glicina_g": "glycine_g",
    "prolina_g": "proline_g",
    "serina_g": "serine_g",
}

TEXT_FIELDS = {"id", "category", "description", "base_name", "preparation", "qualifiers"}

# ---------------------------------------------------------------------------
# Carregamento dos dados
# ---------------------------------------------------------------------------


def _load_csv(filename: str, columns: dict[str, str]) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Arquivo de dados não encontrado: {path}. "
            "Execute 'python scripts/process_taco.py' para gerá-lo."
        )
    df = pd.read_csv(path)
    df = df.rename(columns=columns)
    for col in df.columns:
        if col not in TEXT_FIELDS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["id"] = df["id"].astype(int)
    return df


df_composition = _load_csv("taco_composicao.csv", COMPOSITION_COLUMNS)
df_fatty_acids = _load_csv("taco_acidos_graxos.csv", FATTY_ACIDS_COLUMNS)
df_amino_acids = _load_csv("taco_aminoacidos.csv", AMINO_ACIDS_COLUMNS)


def _fold(texto: str) -> str:
    """Minúsculas sem acentos, para busca insensível a acentuação."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


# Descrições normalizadas (mesmo índice de df_composition), calculadas uma vez
# no import: "acucar" precisa encontrar "açúcar".
_searchable_descriptions = (
    df_composition["description"]
    .str.normalize("NFKD")
    .str.encode("ascii", "ignore")
    .str.decode("ascii")
    .str.lower()
)
_searchable_bases = (
    df_composition["base_name"]
    .str.normalize("NFKD")
    .str.encode("ascii", "ignore")
    .str.decode("ascii")
    .str.lower()
)

# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------


def _row_to_dict(row: pd.Series) -> dict:
    """Converte uma linha em dict seguro para JSON (NaN -> None, floats arredondados)."""
    result: dict = {}
    for key, value in row.to_dict().items():
        if isinstance(value, float):
            result[key] = None if math.isnan(value) else round(value, DECIMAL_PLACES)
        else:
            result[key] = value
    return result


def _get_food(food_id: int) -> dict:
    matches = df_composition[df_composition["id"] == food_id]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Food with id {food_id} not found")
    return _row_to_dict(matches.iloc[0])


def _nutrient_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in TEXT_FIELDS]


def _find_row(df: pd.DataFrame, food_id: int) -> dict | None:
    """Linha do alimento como dict, ou None se a tabela não o contém."""
    matches = df[df["id"] == food_id]
    return None if matches.empty else _row_to_dict(matches.iloc[0])


# ---------------------------------------------------------------------------
# Modelos de resposta (só documentam o OpenAPI; não filtram as respostas)
# ---------------------------------------------------------------------------

_TIPOS_TEXTO = {
    "id": (int, ...),
    "category": (str, ...),
    "description": (str, ...),
    "base_name": (str, ...),
    "preparation": (str | None, None),
    "qualifiers": (str | None, None),
}


def _model_from_columns(name: str, columns: dict[str, str], *, texto: bool = True, **extra):
    campos = {
        campo: _TIPOS_TEXTO.get(campo, (float | None, None))
        for campo in columns.values()
        if texto or campo not in TEXT_FIELDS
    }
    return create_model(name, **campos, **extra)


CompositionOut = _model_from_columns("CompositionOut", COMPOSITION_COLUMNS)
FattyAcidsOut = _model_from_columns("FattyAcidsOut", FATTY_ACIDS_COLUMNS)
AminoAcidsOut = _model_from_columns("AminoAcidsOut", AMINO_ACIDS_COLUMNS)

_FoodFattyAcids = _model_from_columns("FoodFattyAcids", FATTY_ACIDS_COLUMNS, texto=False)
_FoodAminoAcids = _model_from_columns("FoodAminoAcids", AMINO_ACIDS_COLUMNS, texto=False)

FoodOut = create_model(
    "FoodOut",
    __base__=CompositionOut,
    fatty_acids=(_FoodFattyAcids | None, None),
    amino_acids=(_FoodAminoAcids | None, None),
)


# ---------------------------------------------------------------------------
# Modelos de requisição
# ---------------------------------------------------------------------------


class CompareRequest(BaseModel):
    ids: list[int] = Field(min_length=2, description="Food ids to compare")


class SumItem(BaseModel):
    id: int
    grams: float = Field(gt=0, description="Amount in grams")


class SumRequest(BaseModel):
    items: list[SumItem] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Aplicação FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TACO Nutritional Data API",
    description=(
        "REST API for the Brazilian Table of Food Composition (TACO, 4th ed., "
        "NEPA/UNICAMP). All nutrient values refer to 100 g of edible portion."
    ),
    version=API_VERSION,
)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "TACO Nutritional Data API",
        "version": API_VERSION,
        "description": "Brazilian Table of Food Composition (TACO)",
        "total_foods": len(df_composition),
        "docs": "/docs",
        "endpoints": [
            "GET  /health",
            "GET  /categories",
            "GET  /categories/{name}",
            "GET  /foods",
            "GET  /preparations",
            "GET  /foods/{id}",
            "GET  /foods/{id}/fatty-acids",
            "GET  /foods/{id}/amino-acids",
            "POST /foods/compare",
            "POST /foods/sum",
        ],
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "total_foods": len(df_composition)}


# -- Categorias --------------------------------------------------------------


@app.get("/categories", tags=["categories"])
def list_categories():
    counts = (
        df_composition.groupby("category")
        .size()
        .reset_index(name="food_count")
        .sort_values("category")
    )
    return counts.to_dict(orient="records")


@app.get("/categories/{name}", tags=["categories"])
def get_category(name: str):
    matches = df_composition[df_composition["category"].str.lower() == name.lower()]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Category '{name}' not found")
    foods = matches[["id", "description"]].to_dict(orient="records")
    return {
        "category": matches.iloc[0]["category"],
        "food_count": len(foods),
        "foods": foods,
    }


@app.get("/preparations", tags=["categories"])
def list_preparations():
    """Formas de preparo reconhecidas e quantos alimentos há em cada uma."""
    counts = (
        df_composition.groupby("preparation").size().reset_index(name="food_count")
    )
    return counts.sort_values("preparation").to_dict(orient="records")


# -- Alimentos ----------------------------------------------------------------


@app.get("/foods", tags=["foods"])
def list_foods(
    search: str | None = Query(None, description="Search term for food description"),
    base_name: str | None = Query(None, description="Exact base food name, e.g. 'arroz'"),
    preparation: str | None = Query(
        None,
        description="Preparation: cru, cozido, frito, grelhado, assado, refogado, torrado",
    ),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(25, ge=1, le=100, description="Max items to return"),
):
    filtered = df_composition
    if search:
        filtered = filtered[
            _searchable_descriptions.str.contains(_fold(search), na=False, regex=False)
        ]
    if base_name:
        filtered = filtered[_searchable_bases.loc[filtered.index] == _fold(base_name)]
    if preparation:
        filtered = filtered[filtered["preparation"] == _fold(preparation)]
    total = len(filtered)
    page = filtered.iloc[skip : skip + limit][["id", "category", "description"]]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "foods": page.to_dict(orient="records"),
    }


@app.get("/foods/{food_id}", tags=["foods"], responses={200: {"model": FoodOut}})
def get_food(food_id: int):
    food = _get_food(food_id)

    for chave, df in (("fatty_acids", df_fatty_acids), ("amino_acids", df_amino_acids)):
        row = _find_row(df, food_id)
        if row is not None:
            food[chave] = {k: v for k, v in row.items() if k not in TEXT_FIELDS}

    return food


@app.get("/foods/{food_id}/fatty-acids", tags=["foods"], responses={200: {"model": FattyAcidsOut}})
def get_food_fatty_acids(food_id: int):
    _get_food(food_id)  # 404 se o alimento não existe
    row = _find_row(df_fatty_acids, food_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No fatty acid data for food id {food_id}")
    return row


@app.get("/foods/{food_id}/amino-acids", tags=["foods"], responses={200: {"model": AminoAcidsOut}})
def get_food_amino_acids(food_id: int):
    _get_food(food_id)
    row = _find_row(df_amino_acids, food_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No amino acid data for food id {food_id}")
    return row


# -- Comparação e soma ---------------------------------------------------------


@app.post("/foods/compare", tags=["tools"], responses={200: {"model": list[CompositionOut]}})
def compare_foods(body: CompareRequest):
    return [_get_food(fid) for fid in body.ids]


@app.post("/foods/sum", tags=["tools"])
def sum_nutrients(body: SumRequest):
    """Soma os nutrientes de uma lista de alimentos ponderada pela quantidade em gramas.

    Os valores da TACO referem-se a 100 g de parte comestível; cada alimento
    contribui proporcionalmente a ``grams / 100``.

    Nutriente sem dado na TACO não entra na soma. ``missing_values`` informa,
    por nutriente, quantos itens não tinham valor — sem isso o total pareceria
    exato quando na verdade é parcial.
    """
    nutrient_keys = _nutrient_cols(df_composition)
    totals: dict[str, float] = {k: 0.0 for k in nutrient_keys}
    missing: dict[str, int] = {}
    foods_used: list[dict] = []

    for item in body.items:
        food = _get_food(item.id)
        factor = item.grams / 100.0
        foods_used.append(
            {"id": item.id, "description": food["description"], "grams": item.grams}
        )
        for key in nutrient_keys:
            val = food.get(key)
            if val is None:
                missing[key] = missing.get(key, 0) + 1
            else:
                totals[key] += val * factor

    totals = {k: round(v, DECIMAL_PLACES) for k, v in totals.items()}
    return {"items": foods_used, "total_nutrients": totals, "missing_values": missing}

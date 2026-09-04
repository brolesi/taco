"""Gera uma versão estática da API, para servir por CDN (GitHub Pages).

Os dados são somente-leitura e cabem em arquivos: em vez de manter um servidor
no ar, o site publica um JSON por recurso. As respostas saem das **próprias
funções** de ``api.main`` — não há uma segunda implementação do contrato para
divergir da API dinâmica.

Rode como módulo, a partir da raiz do repositório (é o que torna ``api``
importável, o mesmo motivo do ``pythonpath`` no pyproject):

    python -m scripts.build_static_api
    python -m scripts.build_static_api --saida-dir dist/site
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
import unicodedata
from pathlib import Path

from api.main import (
    API_VERSION,
    coverage,
    df_composition,
    df_measures,
    get_category,
    get_food,
    get_food_variants,
    list_categories,
    list_foods,
    list_preparations,
)

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
SAIDA_PADRAO = RAIZ_PROJETO / "dist" / "site"


def _slug(texto: str) -> str:
    """'Bebidas (alcoólicas e não alcoólicas)' -> 'bebidas-alcoolicas-e-nao-alcoolicas'."""
    limpo = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return "-".join("".join(c if c.isalnum() else " " for c in limpo).split())


def _escrever(destino: Path, dados: object) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(dados, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
        newline="\n",
    )


PAGINA_INICIAL = """<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>TACO — API estática</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{{font:16px/1.6 system-ui,sans-serif;max-width:44rem;margin:3rem auto;padding:0 1.2rem}}
 code{{background:#f2f2f2;padding:.1em .35em;border-radius:3px}}
 li{{margin:.3rem 0}}
 a.primary{{display:inline-block;background:#2f6d5e;color:white;padding:10px 16px;border-radius:6px;text-decoration:none;font-weight:600;margin-bottom:2rem}}
</style>
<h1>TACO — API estática</h1>
<p>Tabela Brasileira de Composição de Alimentos (4ª edição, NEPA/UNICAMP) e
medidas caseiras da POF 2008-2009 (IBGE), servidas como arquivos JSON.
Versão {versao}. Sem servidor, sem chave, sem limite de requisições.</p>
<a class="primary" href="api.dc.html">📖 Documentação Interativa</a>
<h3>Endpoints JSON</h3>
<ul>
 <li><code><a href="index.json">index.json</a></code> — metadados e índice</li>
 <li><code><a href="coverage.json">coverage.json</a></code> — cobertura por nutriente</li>
 <li><code><a href="foods.json">foods.json</a></code> — os {n_foods} alimentos</li>
 <li><code><a href="foods/1.json">foods/{{id}}.json</a></code> — composição completa</li>
 <li><code><a href="foods/1/variants.json">foods/{{id}}/variants.json</a></code>
     — outras formas de preparo</li>
 <li><code><a href="categories.json">categories.json</a></code> e
     <code>categories/{{slug}}.json</code></li>
 <li><code><a href="preparations.json">preparations.json</a></code></li>
 <li><code><a href="measures/index.json">measures/index.json</a></code> e
     <code>measures/{{pof_food_id}}.json</code> — medidas caseiras em gramas</li>
</ul>
<p>Os códigos da POF são do IBGE e <strong>não</strong> correspondem aos ids da
TACO; não há equivalência automática entre as duas tabelas.</p>
<p><a href="https://github.com/brolesi/taco">Código, dados e a API dinâmica em
FastAPI</a> · MIT</p>
</html>
"""


def construir(saida_dir: Path) -> int:
    """Escreve todos os arquivos do site e devolve quantos foram gerados."""
    if saida_dir.exists():
        shutil.rmtree(saida_dir)
    saida_dir.mkdir(parents=True)

    ids = [int(i) for i in df_composition["id"]]
    todos = list_foods(search=None, base_name=None, preparation=None, skip=0, limit=len(ids))

    _escrever(saida_dir / "coverage.json", coverage())
    _escrever(saida_dir / "categories.json", list_categories())
    _escrever(saida_dir / "preparations.json", list_preparations())
    _escrever(saida_dir / "foods.json", {"total": todos["total"], "foods": todos["foods"]})

    for categoria in list_categories():
        nome = categoria["category"]
        _escrever(saida_dir / "categories" / f"{_slug(nome)}.json", get_category(nome))

    for food_id in ids:
        _escrever(saida_dir / "foods" / f"{food_id}.json", get_food(food_id))
        _escrever(saida_dir / "foods" / str(food_id) / "variants.json", get_food_variants(food_id))

    indice_medidas = []
    for pof_id, grupo in df_measures.groupby("pof_food_id"):
        registros = [
            {k: (None if v != v else v) for k, v in linha.items()}  # NaN -> None
            for linha in grupo.to_dict(orient="records")
        ]
        _escrever(
            saida_dir / "measures" / f"{pof_id}.json",
            {"pof_food_id": int(pof_id), "measures": registros},
        )
        indice_medidas.append(
            {
                "pof_food_id": int(pof_id),
                "food_description": grupo.iloc[0]["food_description"],
                "measure_count": len(grupo),
            }
        )
    _escrever(
        saida_dir / "measures" / "index.json",
        {"total": len(indice_medidas), "foods": indice_medidas},
    )

    _escrever(
        saida_dir / "index.json",
        {
            "name": "TACO Nutritional Data API (static)",
            "version": API_VERSION,
            "description": "Brazilian Table of Food Composition (TACO) served as static JSON",
            "total_foods": len(ids),
            "total_measures": len(df_measures),
            "source": "https://github.com/brolesi/taco",
            "endpoints": [
                "coverage.json",
                "categories.json",
                "categories/{slug}.json",
                "preparations.json",
                "foods.json",
                "foods/{id}.json",
                "foods/{id}/variants.json",
                "measures/index.json",
                "measures/{pof_food_id}.json",
            ],
        },
    )

    (saida_dir / "index.html").write_text(
        PAGINA_INICIAL.format(versao=API_VERSION, n_foods=len(ids)),
        encoding="utf-8",
        newline="\n",
    )
    # Impede o Jekyll do GitHub Pages de ignorar diretórios iniciados por "_".
    (saida_dir / ".nojekyll").write_text("", encoding="utf-8")

    # Copiar documentação interativa (Design Component)
    docs_dir = RAIZ_PROJETO / "docs"
    for arquivo in ["api.dc.html", "support.js"]:
        src = docs_dir / arquivo
        if src.exists():
            shutil.copy(src, saida_dir / arquivo)

    return sum(1 for _ in saida_dir.rglob("*") if _.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida-dir", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout
    )
    try:
        total = construir(args.saida_dir)
    except Exception:
        logging.exception("Falha ao gerar o site estático em %s", args.saida_dir)
        return 1
    logging.info("Gerados %d arquivos em %s", total, args.saida_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

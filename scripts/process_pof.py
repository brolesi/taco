"""Pipeline da Tabela de Medidas Referidas da POF 2008-2009 (IBGE).

Lê o arquivo Excel original em ``data/raw/pof/`` e exporta um CSV normalizado
(snake_case, valores numéricos) para ``data/processed/pof/``, com o peso em
gramas de cada medida caseira ("colher de sopa", "concha", "fatia") por
alimento.

Uso:
    python scripts/process_pof.py
    python scripts/process_pof.py --entrada tabelamedidas_bd.xls --saida-dir saida/
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ_PROJETO / "data" / "raw" / "pof" / "tabelamedidas_bd.xls"
SAIDA_PADRAO = RAIZ_PROJETO / "data" / "processed" / "pof"
ARQUIVO_SAIDA = "pof_medidas_caseiras.csv"

# A versão "_bd" da planilha traz uma única aba tabular, sem as quebras de
# página da versão de publicação (`tabelamedidas.xls`, com 5 abas).
ABA = "Tab_Medidas Caseiras"
LINHAS_CABECALHO = 5

COLUNAS = [
    "codigo_alimento",
    "descricao_alimento",
    "codigo_preparacao",
    "descricao_preparacao",
    "codigo_medida",
    "descricao_medida",
    "codigo_medida_referencia",
    "descricao_medida_referencia",
    "quantidade_g",
    "codigo_fonte",
    "descricao_fonte",
]

COLUNAS_NUMERICAS = [
    "codigo_alimento",
    "codigo_preparacao",
    "codigo_medida",
    "codigo_medida_referencia",
    "quantidade_g",
    "codigo_fonte",
]


def processar(caminho_xls: Path, saida_dir: Path) -> pd.DataFrame:
    """Lê a planilha da POF, descarta o rodapé e exporta o CSV normalizado."""
    logging.info("Lendo aba '%s' de %s", ABA, caminho_xls)
    df = pd.read_excel(caminho_xls, sheet_name=ABA, header=None, skiprows=LINHAS_CABECALHO)
    df.columns = COLUNAS

    # A última linha é a nota de fonte do IBGE ("Fonte: IBGE, Diretoria de
    # Pesquisas..."); linhas de dados sempre têm código numérico de alimento.
    df = df[pd.to_numeric(df["codigo_alimento"], errors="coerce").notna()]

    for col in COLUNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("codigo_alimento", "codigo_preparacao", "codigo_medida"):
        df[col] = df[col].astype(int)

    saida_csv = saida_dir / ARQUIVO_SAIDA
    df.to_csv(saida_csv, index=False, encoding="utf-8", lineterminator="\n")
    logging.info("Exportado: %s (%d linhas)", saida_csv, len(df))
    return df


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--entrada",
        type=Path,
        default=ENTRADA_PADRAO,
        help="Planilha da POF (padrão: data/raw/pof/tabelamedidas_bd.xls)",
    )
    parser.add_argument(
        "--saida-dir",
        type=Path,
        default=SAIDA_PADRAO,
        help="Diretório do CSV gerado (padrão: data/processed/pof)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )

    if not args.entrada.is_file():
        logging.error("Planilha não encontrada: %s", args.entrada)
        return 1

    args.saida_dir.mkdir(parents=True, exist_ok=True)

    try:
        processar(args.entrada, args.saida_dir)
    except Exception:
        logging.exception("Falha ao processar %s", args.entrada)
        return 1

    logging.info("Processamento concluído com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

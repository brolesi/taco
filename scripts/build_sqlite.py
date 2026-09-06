"""Empacota os CSVs processados em um único arquivo SQLite.

Artefato de conveniência para quem quer o dado sem instalar Python nem subir a
API: um arquivo, consultável em SQL. Não é versionado — é gerado e anexado a
cada release (ver `.github/workflows/release.yml`).

Uso:
    python scripts/build_sqlite.py
    python scripts/build_sqlite.py --saida dist/taco.sqlite
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
PROCESSADOS = RAIZ_PROJETO / "data" / "processed"
SAIDA_PADRAO = RAIZ_PROJETO / "taco.sqlite"

# tabela SQLite -> (CSV de origem, coluna indexada)
TABELAS = {
    "taco_composicao": ("taco/taco_composicao.csv", "numero_alimento"),
    "taco_acidos_graxos": ("taco/taco_acidos_graxos.csv", "numero_alimento"),
    "taco_aminoacidos": ("taco/taco_aminoacidos.csv", "numero_alimento"),
    "pof_medidas_caseiras": ("pof/pof_medidas_caseiras.csv", "codigo_alimento"),
}


def construir(saida: Path, processados: Path = PROCESSADOS) -> Path:
    """Escreve o SQLite a partir dos CSVs processados, sobrescrevendo o destino."""
    faltando = [nome for nome, (csv, _) in TABELAS.items() if not (processados / csv).is_file()]
    if faltando:
        raise FileNotFoundError(
            f"CSVs ausentes para: {', '.join(faltando)}. "
            "Execute 'python scripts/process_taco.py' e 'python scripts/process_pof.py'."
        )

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.unlink(missing_ok=True)

    with sqlite3.connect(saida) as conn:
        for tabela, (csv, indice) in TABELAS.items():
            df = pd.read_csv(processados / csv)
            df.to_sql(tabela, conn, index=False)
            conn.execute(f"CREATE INDEX idx_{tabela}_{indice} ON {tabela}({indice})")
            logging.info("Tabela %s: %d linhas", tabela, len(df))

        # Procedência junto do dado: quem baixa só o arquivo perde o README.
        conn.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        conn.executemany(
            "INSERT INTO metadados VALUES (?, ?)",
            [
                ("fonte_taco", "TACO 4a edicao (NEPA/UNICAMP)"),
                ("fonte_pof", "Tabela de Medidas Referidas, POF 2008-2009 (IBGE)"),
                ("repositorio", "https://github.com/brolesi/taco"),
                ("licenca", "MIT (codigo); dados de fontes publicas citadas acima"),
                ("gerado_em", date.today().isoformat()),
                ("unidade", "valores por 100 g de parte comestivel"),
            ],
        )

    logging.info("Exportado: %s (%.1f MB)", saida, saida.stat().st_size / 1e6)
    return saida


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="Arquivo .sqlite gerado")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )

    try:
        construir(args.saida)
    except Exception:
        logging.exception("Falha ao gerar %s", args.saida)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

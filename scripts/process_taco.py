"""Pipeline de processamento da planilha TACO (4ª edição, NEPA/UNICAMP).

Lê o arquivo Excel original em ``data/raw/taco/`` e exporta CSVs normalizados
(snake_case, valores numéricos, coluna de categoria) para
``data/processed/taco/``.

Uso:
    python scripts/process_taco.py
    python scripts/process_taco.py --entrada planilha.xls --saida-dir saida/
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ_PROJETO / "data" / "raw" / "taco" / "Taco_4a_edicao_2011.xls"
SAIDA_PADRAO = RAIZ_PROJETO / "data" / "processed" / "taco"

# Valor usado no lugar de "Tr" (traço: quantidade abaixo do limite de
# quantificação). Mantido > 0 para diferenciar de ausência de dado (NaN).
VALOR_TRACO = 1e-5

# Rótulos das linhas separadoras de categoria presentes nas abas da planilha.
# A categoria de cada alimento é derivada dessas linhas (forward-fill), pois é
# a única fonte confiável — as faixas de numeração não são contíguas por
# categoria.
CATEGORIAS_PLANILHA = [
    "Cereais e derivados",
    "Verduras, hortaliças e derivados",
    "Frutas e derivados",
    "Gorduras e óleos",
    "Pescados e frutos do mar",
    "Carnes e derivados",
    "Leite e derivados",
    "Bebidas (alcoólicas e não alcoólicas)",
    "Ovos e derivados",
    "Produtos açucarados",
    "Miscelâneas",
    "Outros alimentos industrializados",
    "Alimentos preparados",
    "Leguminosas e derivados",
    "Nozes e sementes",
]


# Formas de preparo reconhecidas nas descrições, mapeadas para uma forma
# canônica (as descrições variam em gênero: "cru"/"crua"). Nenhuma descrição
# da TACO contém dois preparos, então a primeira ocorrência é suficiente.
PREPAROS = {
    "cru": "cru",
    "crua": "cru",
    "cozido": "cozido",
    "cozida": "cozido",
    "pré-cozido": "cozido",
    "pré-cozida": "cozido",
    "frito": "frito",
    "frita": "frito",
    "assado": "assado",
    "assada": "assado",
    "grelhado": "grelhado",
    "grelhada": "grelhado",
    "refogado": "refogado",
    "refogada": "refogado",
    "torrado": "torrado",
    "torrada": "torrado",
    "tostado": "torrado",
    "tostada": "torrado",
}


def facetar_descricao(descricao: str) -> tuple[str, str | None, str | None]:
    """Separa a descrição da TACO em (base, preparo, qualificadores).

    As descrições são facetadas por vírgula ("Arroz, integral, cozido"): o
    primeiro termo é o alimento-base, um dos demais pode ser uma forma de
    preparo conhecida (canonizada por ``PREPAROS``) e o restante são
    qualificadores, preservados na ordem original.
    """
    termos = [t.strip() for t in descricao.split(",")]
    base, resto = termos[0], termos[1:]

    preparo = None
    qualificadores = []
    for termo in resto:
        canonico = PREPAROS.get(termo.lower())
        if canonico is not None and preparo is None:
            preparo = canonico
        else:
            qualificadores.append(termo)

    return base, preparo, ", ".join(qualificadores) or None


@dataclass
class AbaConfig:
    """Configuração de processamento de uma aba da planilha."""

    sheet_name: str
    colunas: list[str]
    arquivo_saida: str
    coluna_duplicada: str = "numero_alimento_2"
    linhas_cabecalho: int = 3
    # Só a aba de composição recebe as facetas: é a entidade "alimento" da API;
    # as outras repetem as mesmas descrições.
    facetar: bool = False


# A aba de composição deve ser a primeira: ela fornece o mapa id -> categoria
# usado pelas abas sem linhas separadoras (aminoácidos).
ABAS: list[AbaConfig] = [
    AbaConfig(
        sheet_name="CMVCol taco3",
        arquivo_saida="taco_composicao.csv",
        facetar=True,
        colunas=[
            "numero_alimento",
            "descricao",
            "umidade_pct",
            "energia_kcal",
            "energia_kj",
            "proteina_g",
            "lipideos_g",
            "colesterol_mg",
            "carboidrato_g",
            "fibra_g",
            "cinzas_g",
            "calcio_mg",
            "magnesio_mg",
            "numero_alimento_2",
            "manganes_mg",
            "fosforo_mg",
            "ferro_mg",
            "sodio_mg",
            "potassio_mg",
            "cobre_mg",
            "zinco_mg",
            "retinol_mcg",
            "RE_mcg",
            "RAE_mcg",
            "tiamina_mg",
            "riboflavina_mg",
            "piridoxina_mg",
            "niacina_mg",
            "vitamina_c_mg",
        ],
    ),
    AbaConfig(
        sheet_name="AGtaco3",
        arquivo_saida="taco_acidos_graxos.csv",
        colunas=[
            "numero_alimento",
            "descricao",
            "saturados_g",
            "monoinsaturados_g",
            "poliinsaturados_g",
            "c12_0_g",
            "c14_0_g",
            "c16_0_g",
            "c18_0_g",
            "c20_0_g",
            "c22_0_g",
            "c24_0_g",
            "numero_alimento_2",
            "c14_1_g",
            "c16_1_g",
            "c18_1_g",
            "c20_1_g",
            "c18_2n6_g",
            "c18_3n3_g",
            "c20_4_g",
            "c20_5_g",
            "c22_5_g",
            "c22_6_g",
            "c18_1t_g",
            "c18_2t_g",
        ],
    ),
    AbaConfig(
        sheet_name="Aminoácidos TACO3",
        arquivo_saida="taco_aminoacidos.csv",
        colunas=[
            "numero_alimento",
            "descricao",
            "triptofano_g",
            "treonina_g",
            "isoleucina_g",
            "leucina_g",
            "lisina_g",
            "metionina_g",
            "cistina_g",
            "fenilalanina_g",
            "tirosina_g",
            "numero_alimento_2",
            "valina_g",
            "arginina_g",
            "histidina_g",
            "alanina_g",
            "acido_aspartico_g",
            "acido_glutamico_g",
            "glicina_g",
            "prolina_g",
            "serina_g",
        ],
    ),
]


def processar_aba(
    caminho_xls: Path,
    config: AbaConfig,
    saida_dir: Path,
    mapa_categorias: dict[int, str] | None = None,
) -> pd.DataFrame:
    """Processa uma aba da planilha TACO, normaliza e exporta para CSV.

    A categoria vem das linhas separadoras da própria aba (forward-fill).
    Abas sem separadores (aminoácidos) usam *mapa_categorias* (id -> categoria),
    construído a partir da aba de composição.
    """
    logging.info("Lendo aba '%s' de %s", config.sheet_name, caminho_xls)
    df = pd.read_excel(caminho_xls, sheet_name=config.sheet_name, header=None)
    df = df.iloc[config.linhas_cabecalho :]
    df.columns = config.colunas

    # Deriva a categoria das linhas separadoras antes de removê-las.
    rotulos = df["numero_alimento"]
    df["categoria"] = rotulos.where(rotulos.isin(CATEGORIAS_PLANILHA)).ffill()

    # Mantém apenas linhas de dados (número do alimento é inteiro); isso
    # descarta separadores de categoria, legendas e notas de rodapé.
    df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
    df["numero_alimento"] = df["numero_alimento"].astype(int)

    if mapa_categorias is not None:
        df["categoria"] = df["categoria"].fillna(
            df["numero_alimento"].map(mapa_categorias)
        )

    df = df.replace("Tr", VALOR_TRACO)

    if config.coluna_duplicada in df.columns:
        df = df.drop(columns=[config.coluna_duplicada])

    colunas_numericas = df.columns.drop(["numero_alimento", "descricao", "categoria"])
    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if config.facetar:
        facetas = df["descricao"].map(facetar_descricao)
        df["base"] = [f[0] for f in facetas]
        df["preparo"] = [f[1] for f in facetas]
        df["qualificadores"] = [f[2] for f in facetas]

    # Mantém 'categoria' como última coluna.
    df = df[[c for c in df.columns if c != "categoria"] + ["categoria"]]

    saida_csv = saida_dir / config.arquivo_saida
    # lineterminator fixo: sem isso o pandas usa os.linesep e os CSVs sairiam
    # com CRLF no Windows e LF no Linux, quebrando a comparação byte a byte.
    df.to_csv(saida_csv, index=False, encoding="utf-8", lineterminator="\n")
    logging.info("Exportado: %s (%d linhas)", saida_csv, len(df))
    return df


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--entrada",
        type=Path,
        default=ENTRADA_PADRAO,
        help="Planilha TACO original (padrão: data/raw/taco/Taco_4a_edicao_2011.xls)",
    )
    parser.add_argument(
        "--saida-dir",
        type=Path,
        default=SAIDA_PADRAO,
        help="Diretório dos CSVs gerados (padrão: data/processed/taco)",
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

    falhas = 0
    mapa_categorias: dict[int, str] | None = None
    for config in ABAS:
        try:
            df = processar_aba(args.entrada, config, args.saida_dir, mapa_categorias)
            if mapa_categorias is None:
                mapa_categorias = dict(
                    zip(df["numero_alimento"], df["categoria"], strict=True)
                )
        except Exception:
            logging.exception("Falha ao processar a aba '%s'", config.sheet_name)
            falhas += 1

    if falhas:
        logging.error("%d aba(s) falharam.", falhas)
        return 1

    logging.info("Processamento concluído com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

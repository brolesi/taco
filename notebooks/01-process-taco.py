import pandas as pd
import logging
import sys
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

categoria_ranges = {
    "Cereais e derivados": (1, 73),
    "Verduras, hortaliças e derivados": (74, 183),
    "Frutas e derivados": (184, 290),
    "Gorduras e óleos": (291, 306),
    "Pescados e frutos do mar": (307, 365),
    "Carnes e derivados": (366, 502),
    "Leite e derivados": (503, 531),
    "Bebidas": (532, 547),
    "Ovos e derivados": (548, 555),
    "Produtos açucarados": (556, 580),
    "Miscelâneas": (581, 591),
    "Outros industrializados": (592, 602),
    "Alimentos preparados": (603, 639),
    "Leguminosas e derivados": (640, 674),
    "Nozes e sementes": (675, 697),
}


def get_categoria(num: int) -> str:
    """Retorna a categoria do alimento dado seu número."""
    for cat, (inicio, fim) in categoria_ranges.items():
        if inicio <= num <= fim:
            return cat
    return "Outros"


def processar_aba(
    caminho_xls: str,
    sheet_name: str,
    colunas: List[str],
    saida_csv: str,
    remover_categorias: bool = True,
    coluna_duplicada: str = "numero_alimento_2",
    substituir_tr: bool = True,
    skiprows: int = 3,
) -> pd.DataFrame:
    """
    Processa uma aba do Excel TACO, limpa e exporta para CSV.
    """
    try:
        logging.info(f"Lendo aba '{sheet_name}' do arquivo {caminho_xls}")
        df = pd.read_excel(caminho_xls, sheet_name=sheet_name, header=None)
        df = df.iloc[skiprows:]
        df.columns = colunas

        if remover_categorias:
            df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
            df["numero_alimento"] = df["numero_alimento"].astype(int)
        else:
            categorias = [
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
                "Legenda",
            ]
            df = df[~df["numero_alimento"].isin(categorias)]
            df = df[~df["numero_alimento"].astype(str).str.match(r"^[†\*]")]
            df = df[df["numero_alimento"].notna()]
            df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
            df["numero_alimento"] = df["numero_alimento"].astype(int)

        if substituir_tr:
            df = df.replace("Tr", 1e-5)

        if coluna_duplicada in df.columns:
            df = df.drop(columns=[coluna_duplicada])

        colunas_numericas = df.columns.drop(["numero_alimento", "descricao"])
        for col in colunas_numericas:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["categoria"] = df["numero_alimento"].apply(get_categoria)
        df.to_csv(saida_csv, index=False, encoding="utf-8")
        logging.info(f"Exportado: {saida_csv} ({len(df)} linhas)")
        return df
    except Exception as e:
        logging.error(f"Erro ao processar aba '{sheet_name}': {e}")
        raise


def main():
    """Executa o pipeline de processamento das abas do TACO."""
    caminho_xls = "../data/raw/taco/Taco_4a_edicao_2011.xls"

    abas = [
        {
            "sheet_name": "CMVCol taco3",
            "colunas": [
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
            "saida_csv": "../data/processed/taco/taco_composicao.csv",
            "remover_categorias": False,
        },
        {
            "sheet_name": "AGtaco3",
            "colunas": [
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
            "saida_csv": "../data/processed/taco/taco_acidos_graxos.csv",
            "remover_categorias": True,
        },
        {
            "sheet_name": "Aminoácidos TACO3",
            "colunas": [
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
            "saida_csv": "../data/processed/taco/taco_aminoacidos.csv",
            "remover_categorias": True,
        },
    ]

    for aba in abas:
        try:
            processar_aba(
                caminho_xls=caminho_xls,
                sheet_name=aba["sheet_name"],
                colunas=aba["colunas"],
                saida_csv=aba["saida_csv"],
                remover_categorias=aba["remover_categorias"],
            )
        except Exception as e:
            logging.error(f"Falha ao processar {aba['sheet_name']}: {e}")


if __name__ == "__main__":
    main()

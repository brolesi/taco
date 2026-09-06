"""Testes do pipeline de processamento da planilha TACO."""

import pandas as pd
import pytest

from scripts.build_sqlite import TABELAS, construir
from scripts.process_pof import ARQUIVO_SAIDA as POF_ARQUIVO
from scripts.process_pof import ENTRADA_PADRAO as POF_ENTRADA
from scripts.process_pof import SAIDA_PADRAO as POF_SAIDA
from scripts.process_pof import main as pof_main
from scripts.process_taco import ENTRADA_PADRAO, SAIDA_PADRAO, facetar_descricao, main

CSVS = ("taco_composicao.csv", "taco_acidos_graxos.csv", "taco_aminoacidos.csv")


@pytest.mark.skipif(
    not ENTRADA_PADRAO.is_file(), reason="planilha TACO original ausente em data/raw/"
)
def test_csvs_versionados_sao_reproduziveis(tmp_path):
    # Os CSVs em data/processed/ devem sair byte a byte do pipeline: se este
    # teste falhar, regenere-os e commite junto com a mudança no pipeline.
    assert main(["--saida-dir", str(tmp_path)]) == 0
    for nome in CSVS:
        assert (tmp_path / nome).read_bytes() == (SAIDA_PADRAO / nome).read_bytes(), nome


def test_entrada_inexistente_retorna_erro(tmp_path):
    assert main(["--entrada", str(tmp_path / "nao-existe.xls")]) == 1


def test_facetar_descricao():
    assert facetar_descricao("Arroz, integral, cozido") == ("Arroz", "cozido", "integral")
    # Gênero é canonizado: "crua" e "cru" devem virar o mesmo preparo.
    assert facetar_descricao("Alface, crespa, crua")[1] == "cru"
    assert facetar_descricao("Arroz, tipo 1, cru")[1] == "cru"
    # Sem preparo declarado e sem qualificadores.
    assert facetar_descricao("Acarajé") == ("Acarajé", None, None)
    # Vários qualificadores preservam a ordem original.
    assert facetar_descricao("Carne, bovina, acém, moída, crua") == (
        "Carne",
        "cru",
        "bovina, acém, moída",
    )


@pytest.mark.skipif(not POF_ENTRADA.is_file(), reason="planilha da POF ausente em data/raw/pof/")
def test_csv_da_pof_e_reproduzivel(tmp_path):
    assert pof_main(["--saida-dir", str(tmp_path)]) == 0
    assert (tmp_path / POF_ARQUIVO).read_bytes() == (POF_SAIDA / POF_ARQUIVO).read_bytes()


def test_pof_descarta_rodape_da_planilha():
    # A última linha da planilha é a nota de fonte do IBGE, sem código de
    # alimento: ela não pode virar registro.
    df = pd.read_csv(POF_SAIDA / POF_ARQUIVO)
    assert len(df) == 11801
    assert df["codigo_alimento"].astype(str).str.fullmatch(r"\d{7}").all()


def test_pof_entrada_inexistente_retorna_erro(tmp_path):
    assert pof_main(["--entrada", str(tmp_path / "nao-existe.xls")]) == 1


def test_sqlite_reune_os_quatro_csvs(tmp_path):
    import sqlite3

    destino = construir(tmp_path / "taco.sqlite")
    with sqlite3.connect(destino) as conn:
        tabelas = {n for (n,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert tabelas == set(TABELAS) | {"metadados"}
        assert conn.execute("SELECT count(*) FROM taco_composicao").fetchone()[0] == 597
        assert conn.execute("SELECT count(*) FROM pof_medidas_caseiras").fetchone()[0] == 11801
        # A procedência viaja junto: quem baixa só o arquivo não tem o README.
        meta = dict(conn.execute("SELECT chave, valor FROM metadados"))
        assert "TACO" in meta["fonte_taco"] and meta["repositorio"].startswith("https://")

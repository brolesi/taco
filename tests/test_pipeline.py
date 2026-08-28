"""Testes do pipeline de processamento da planilha TACO."""

import pytest

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

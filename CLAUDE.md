# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

Nesta máquina não há `python`/`py` no PATH (apenas stubs da Microsoft Store). Use o
venv do projeto: `.venv\Scripts\python.exe` (se não existir, crie-o com o Python do
Anaconda em `C:\Users\suzan\anaconda3\python.exe -m venv .venv` e instale
`requirements-dev.txt`).

```powershell
.venv\Scripts\python.exe -m pytest                       # todos os testes
.venv\Scripts\python.exe -m pytest tests/test_api.py::test_get_food  # um teste
.venv\Scripts\python.exe -m ruff check .                 # lint (CI falha se não passar)
.venv\Scripts\python.exe scripts\process_taco.py         # regenera os CSVs processados
.venv\Scripts\python.exe -m uvicorn api.main:app --reload  # sobe a API (ou run.bat)
```

O CI (`.github/workflows/ci.yml`) roda `ruff check .` e `pytest` em cada push/PR
para `main`. Configuração de ruff/pytest em `pyproject.toml` (linha de 100 chars;
`pythonpath = ["."]` é o que permite `from api.main import app` nos testes).

## Arquitetura

Fluxo de dados em três estágios; a API é servida a partir de CSVs versionados, não
de banco de dados:

1. **`data/raw/`** — fontes originais imutáveis (planilha TACO `.xls`, tabelas POF).
   Nunca editar.
2. **`scripts/process_taco.py`** — pipeline que lê as 3 abas da planilha TACO e
   exporta `data/processed/taco/taco_{composicao,acidos_graxos,aminoacidos}.csv`
   (colunas pt-BR snake_case). Os CSVs processados são versionados e devem ser
   **reproduzíveis byte a byte** pelo pipeline — nunca editá-los à mão; se mudar o
   pipeline, regenere e commite os CSVs junto. Eles usam LF em qualquer SO
   (`lineterminator="''' + BS + '''n"` no `to_csv` mais `-text` no `.gitattributes`);
   não reverta isso, ou a saída passa a depender do sistema operacional.
3. **`api/main.py`** — FastAPI que carrega os 3 CSVs em DataFrames no import do
   módulo e traduz as colunas para o contrato público em inglês
   (`COMPOSITION_COLUMNS` etc.). Mudanças de contrato devem ser refletidas em
   `docs/dicionario-dados.md` e registradas no `CHANGELOG.md`.

`scripts/process_pof.py` é o segundo pipeline, independente: lê
`data/raw/pof/tabelamedidas_bd.xls` e gera
`data/processed/pof/pof_medidas_caseiras.csv` (medidas caseiras em gramas).
Os códigos de alimento do IBGE **não** correspondem aos da TACO e não há
crosswalk entre as duas — não invente um por semelhança de nome (só 13% dos
alimentos da POF têm base idêntica na TACO, e a maioria é ambígua quanto a
variedade e preparo).

### Regras de domínio não óbvias

- **Categoria dos alimentos**: derivada das linhas separadoras das abas da
  planilha via forward-fill, **antes** de filtrá-las. Não inferir por faixas de
  `numero_alimento` — a numeração não é contígua por categoria (bug já corrigido;
  há teste de regressão com o alimento 561). A aba de aminoácidos não tem
  separadores, então recebe a categoria por join com a aba de composição — por
  isso a aba de composição precisa ser processada primeiro (ordem de `ABAS`).
- **Valor "Tr" (traço)**: convertido para `1e-5` nos CSVs, para distinguir de
  dado ausente (NaN). Por isso a API arredonda respostas em 5 casas decimais
  (`DECIMAL_PLACES`) — não reduza, ou o traço vira zero.
- Todos os valores nutricionais referem-se a 100 g de parte comestível;
  `/foods/sum` pondera por `grams / 100`.
- Os testes dependem dos CSVs processados existirem (o `TestClient` importa
  `api.main`, que carrega os arquivos no import).

## Convenções

- Documentação e docstrings em pt-BR; nomes de campos da API em inglês (contrato
  público — não renomear sem registrar no CHANGELOG).
- `CHANGELOG.md` segue Keep a Changelog / SemVer; a versão da API está em
  `api/main.py` (`API_VERSION`) e em `pyproject.toml`.

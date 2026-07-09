# Changelog

Este arquivo segue o formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.1.0] - 2026-07-09

### Corrigido

- **Categorias dos alimentos nos CSVs `taco_*.csv`**: eram inferidas por faixas
  de `numero_alimento` incorretas (ex.: "Feijão, carioca, cozido" aparecia como
  "Produtos açucarados" e "Feijoada" como "Bebidas"). Agora são derivadas das
  linhas separadoras da própria planilha; na aba de aminoácidos, obtidas por
  cruzamento com a aba de composição.
- Faixa incorreta de "Nozes e sementes" no guia de normalização
  (`references/guia_normalizacao_taco.md`), cuja seção de categorias foi
  reescrita para refletir a abordagem correta.

### Alterado

- A API passou a ler os CSVs canônicos gerados pelo pipeline
  (`taco_composicao.csv`, `taco_acidos_graxos.csv`, `taco_aminoacidos.csv`),
  eliminando a dependência dos CSVs legados com cabeçalhos no estilo R.
- Pipeline movido de `notebooks/01-process-taco.py` para
  `scripts/process_taco.py`, com caminhos resolvidos a partir da raiz do
  repositório (funciona de qualquer diretório), interface de linha de comando
  (`--entrada`, `--saida-dir`) e código de saída diferente de zero em caso de falha.
- `/foods/sum` agora arredonda apenas o total final (antes arredondava a cada
  parcela, acumulando erro).
- A busca em `/foods?search=` trata o termo como texto literal (antes,
  caracteres especiais de regex podiam quebrar a consulta).
- Validações de `/foods/compare` (mínimo de 2 ids) e `/foods/sum` (ao menos
  1 item, gramas > 0) movidas para os modelos Pydantic (agora retornam 422).

### Adicionado

- Endpoint `GET /health`.
- Testes automatizados da API (`tests/`) e CI no GitHub Actions (lint + testes).
- `requirements.txt` / `requirements-dev.txt` na raiz, `pyproject.toml`
  (configuração de Ruff e pytest), `.gitignore` e licença MIT.
- Documentação: dicionário de dados (`docs/dicionario-dados.md`),
  guia de contribuição (`CONTRIBUTING.md`) e README reescrito.
- Arquivos de metadados e higiene: `CITATION.cff` (botão "Cite this
  repository" do GitHub), `.gitattributes` (normalização de quebras de linha),
  `.editorconfig`, `.github/dependabot.yml` (atualizações mensais de
  dependências) e `CLAUDE.md`.

### Removido

- CSVs legados duplicados em `data/processed/taco/` (`alimentos.csv`,
  `acidos-graxos.csv`, `aminoacidos.csv`) — substituídos pelos arquivos
  `taco_*.csv` gerados pelo pipeline.
- `api/requirements.txt` (consolidado no `requirements.txt` da raiz).

## [1.0.0] - 2026-02-13

- Versão inicial: dados originais (TACO, POF, Guia Alimentar), pipeline de
  processamento e API REST (FastAPI).

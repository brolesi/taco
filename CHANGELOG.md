# Changelog

Este arquivo segue o formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.3.0] - não lançado

### Adicionado

- **Facetas da descrição** nos CSVs e na API: `base` (`base_name`), `preparo`
  (`preparation`) e `qualificadores` (`qualifiers`). As descrições da TACO já
  eram facetadas por vírgula ("Arroz, integral, cozido"); o pipeline agora as
  separa e canoniza a forma de preparo ("crua" e "cru" viram `cru`), cobrindo
  364 dos 597 alimentos.
- Filtros `base_name` e `preparation` em `GET /foods` (ambos insensíveis a
  acento e caixa) e endpoint `GET /preparations` com a contagem por preparo.

### Corrigido

- Os CSVs processados passaram a usar LF em qualquer sistema operacional. O
  `to_csv` seguia `os.linesep`, então o mesmo pipeline gerava bytes diferentes
  no Windows e no Linux; a comparação byte a byte só não acusava porque a
  normalização do Git desfazia a diferença no caminho de volta.

## [1.2.0] - 2026-08-28

### Adicionado

- `/foods/sum` passou a devolver `missing_values`: quantos itens não tinham
  valor para cada nutriente. Dado ausente na TACO nunca entrou na soma, mas o
  total aparentava ser exato quando era parcial.
- Testes do pipeline (`tests/test_pipeline.py`): os CSVs versionados em
  `data/processed/taco/` são comparados byte a byte com a saída do pipeline.

### Alterado

- A busca em `/foods?search=` ignora acentuação: `acucar` encontra `açúcar`.
- `/docs` passou a documentar o schema das respostas de `/foods/{id}`,
  `/foods/{id}/fatty-acids`, `/foods/{id}/amino-acids` e `/foods/compare`
  (modelos gerados a partir dos mapas de colunas; as respostas em si não mudam).

### Removido

- `data/interim/taco/` — exportações legadas (separador `;`, decimal com
  vírgula) que nenhum código consumia. Continuam disponíveis no histórico do
  Git.

## [1.1.0] - 2026-07-09

A API REST foi publicada nesta versão; os itens em "Alterado" que descrevem
endpoints referem-se ao protótipo anterior, que não chegou a ser versionado.

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

- A API lê os CSVs canônicos gerados pelo pipeline (`taco_composicao.csv`,
  `taco_acidos_graxos.csv`, `taco_aminoacidos.csv`), eliminando a dependência
  dos CSVs legados com cabeçalhos no estilo R.
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

- **API REST em FastAPI** (`api/main.py`): consulta, comparação e soma de
  nutrientes a partir dos CSVs canônicos.
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

## [1.0.0] - 2026-01-17

- Versão inicial, apenas dados: fontes originais (TACO, POF, Guia Alimentar),
  pipeline de processamento (`notebooks/01-process-taco.py`) e CSVs
  normalizados em `data/processed/taco/`. A API REST só veio na 1.1.0.

[1.2.0]: https://github.com/brolesi/taco/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/brolesi/taco/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/brolesi/taco/releases/tag/v1.0.0

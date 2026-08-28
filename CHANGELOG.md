# Changelog

Este arquivo segue o formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.7.0] - 2026-08-28

### Adicionado

- DOI do Zenodo (`10.5281/zenodo.22145839`, conceitual) no `CITATION.cff`, no
  BibTeX do README e como badge. Cada release passa a ser citável por DOI
  próprio; a 1.6.0 é `10.5281/zenodo.22145840`.
- CORS liberado na API dinâmica (`GET`/`POST`, qualquer origem): dados públicos
  e somente-leitura, o mesmo cabeçalho que o GitHub Pages já devolve na versão
  estática. Sem isso, quem sobe a API local não consegue consumi-la de um
  front-end.
- O CI passou a rodar também no Windows. O teste de reprodutibilidade compara
  bytes, e é no Windows que a quebra de linha nativa difere — sem essa matriz,
  reverter o `lineterminator` do pipeline passaria despercebido.

### Alterado

- `pandas` e `xlrd` ganharam teto de major em `requirements.txt`: são eles que
  determinam os bytes dos CSVs gerados.

## [1.6.0] - 2026-08-28

### Adicionado

- **API estática** publicada no GitHub Pages
  (<https://brolesi.github.io/taco/>): um JSON por recurso, gerado por
  `scripts/build_static_api.py` e publicado a cada push na `main`
  (`.github/workflows/pages.yml`). As respostas saem das próprias funções de
  `api.main`, então não existe uma segunda implementação do contrato para
  divergir — há teste comparando as duas.
- `.zenodo.json` com os metadados do dataset, para o DOI emitido a cada release
  depois que o repositório for habilitado no Zenodo.

### Corrigido

- A contagem de alimentos da POF era 1.120 na documentação; são **1.119**
  códigos distintos (1.124 pares código+descrição). Os números de
  correspondência com a TACO passam a 147 alimentos com base idêntica e 82
  inequívocos.

## [1.5.0] - 2026-08-28

### Adicionado

- `GET /coverage`: quantos alimentos têm dado para cada nutriente, pior
  cobertura primeiro. Mais da metade da TACO não tem vitamina A (42,7%) nem
  colesterol (44,6%), e aminoácidos existem para só 26 alimentos — informação
  que decide se a tabela serve para um uso e que a publicação original não
  apresenta assim. A mesma cobertura está no dicionário de dados.
- `scripts/build_sqlite.py` e o workflow `release.yml`: cada release passa a
  ter um `taco.sqlite` anexado, com as quatro tabelas e uma tabela de
  `metadados` com procedência. O arquivo não é versionado.

## [1.4.0] - 2026-08-28

### Adicionado

- **Pipeline da POF/IBGE** (`scripts/process_pof.py`): normaliza a Tabela de
  Medidas Referidas em `data/processed/pof/pof_medidas_caseiras.csv` — 11.801
  registros com o peso em gramas de 103 medidas caseiras para 1.119 alimentos.
  A planilha em `data/raw/pof/` estava versionada desde a 1.0.0 sem nenhum
  pipeline que a consumisse.
- Endpoints `GET /measures` (busca por alimento e filtro por medida, ambos sem
  acento) e `GET /measures/types`. `GET /health` passou a informar
  `total_measures`.
- `GET /foods/{id}/variants`: o mesmo alimento nas outras formas de preparo
  (97 grupos, 208 alimentos), agrupado pelas facetas da 1.3.0. Devolve
  `moisture_pct` junto, mas **não** calcula retenção de nutrientes: a TACO
  amostra cru e cozido de forma independente e não fornece fator de
  rendimento, então a conta por 100 g mede a água incorporada, não a perda.

### Alterado

- O dicionário de dados agora cobre os dois pipelines e registra por que não há
  equivalência automática entre os códigos da POF e os da TACO.

## [1.3.0] - 2026-08-28

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

[1.7.0]: https://github.com/brolesi/taco/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/brolesi/taco/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/brolesi/taco/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/brolesi/taco/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/brolesi/taco/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/brolesi/taco/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/brolesi/taco/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/brolesi/taco/releases/tag/v1.0.0

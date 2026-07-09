# TACO — Tabela Brasileira de Composição de Alimentos

[![CI](https://github.com/brolesi/taco/actions/workflows/ci.yml/badge.svg)](https://github.com/brolesi/taco/actions/workflows/ci.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE)

Dados normalizados e API REST da **Tabela Brasileira de Composição de Alimentos
(TACO, 4ª edição, NEPA/UNICAMP)**, acompanhados de fontes complementares
(Guia Alimentar para a População Brasileira e Tabela de Medidas Referidas da POF/IBGE).

O repositório oferece:

- **Pipeline reproduzível** ([`scripts/process_taco.py`](scripts/process_taco.py)) que
  converte a planilha original da TACO em CSVs limpos e normalizados;
- **CSVs prontos para uso** em [`data/processed/taco/`](data/processed/taco/)
  (composição centesimal, ácidos graxos e aminoácidos);
- **API REST** ([FastAPI](https://fastapi.tiangolo.com/)) para consulta, comparação
  e soma de nutrientes.

## Estrutura do projeto

```
taco/
├── api/                  # API REST (FastAPI)
├── data/
│   ├── raw/              # Fontes originais, imutáveis (TACO .xls, POF .xls)
│   ├── interim/          # Exportações intermediárias legadas (CSV ; decimal vírgula)
│   └── processed/taco/   # CSVs canônicos gerados pelo pipeline
├── docs/                 # Dicionário de dados
├── references/           # Documentos originais (PDFs) e guia de normalização
├── scripts/              # Pipeline de processamento
└── tests/                # Testes da API
```

## Início rápido

Requer **Python 3.10+**.

```bash
git clone https://github.com/brolesi/taco.git
cd taco

python -m venv .venv
# Windows: .venv\Scripts\activate  |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### Subir a API

```bash
uvicorn api.main:app --reload
```

No Windows, o atalho [`run.bat`](run.bat) faz o mesmo. A documentação interativa
(Swagger) fica em <http://127.0.0.1:8000/docs>.

### Regenerar os CSVs processados

Os CSVs já estão versionados; execute o pipeline apenas se quiser reproduzi-los
a partir da planilha original:

```bash
python scripts/process_taco.py
```

## API

Todos os valores nutricionais referem-se a **100 g de parte comestível**.
Os nomes de campo da API estão mapeados no
[dicionário de dados](docs/dicionario-dados.md).

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Metadados da API |
| GET | `/health` | Verificação de saúde |
| GET | `/categories` | Categorias e contagem de alimentos |
| GET | `/categories/{nome}` | Alimentos de uma categoria |
| GET | `/foods?search=&skip=&limit=` | Lista/busca paginada de alimentos |
| GET | `/foods/{id}` | Composição completa de um alimento |
| GET | `/foods/{id}/fatty-acids` | Perfil de ácidos graxos |
| GET | `/foods/{id}/amino-acids` | Perfil de aminoácidos |
| POST | `/foods/compare` | Compara a composição de 2+ alimentos |
| POST | `/foods/sum` | Soma nutrientes ponderados por gramas |

Exemplo:

```bash
curl "http://127.0.0.1:8000/foods?search=arroz&limit=3"
curl -X POST "http://127.0.0.1:8000/foods/sum" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 1, "grams": 150}, {"id": 2, "grams": 80}]}'
```

## Dados

| Arquivo | Conteúdo | Registros |
|---|---|---|
| `data/processed/taco/taco_composicao.csv` | Composição centesimal, minerais e vitaminas | 597 |
| `data/processed/taco/taco_acidos_graxos.csv` | Perfil de ácidos graxos | 423 |
| `data/processed/taco/taco_aminoacidos.csv` | Perfil de aminoácidos | 26 |

Detalhes de colunas, unidades e valores especiais (`Tr`, `NA`) no
[dicionário de dados](docs/dicionario-dados.md). As decisões de normalização
estão documentadas em
[references/guia_normalizacao_taco.md](references/guia_normalizacao_taco.md).

Os arquivos em `data/interim/taco/` são exportações intermediárias legadas
(separador `;`, decimal com vírgula), mantidas apenas para referência histórica.

## Desenvolvimento

```bash
pip install -r requirements-dev.txt
ruff check .   # lint
pytest         # testes
```

O CI (GitHub Actions) executa lint e testes em cada push/PR para `main`.
Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo completo e
[CHANGELOG.md](CHANGELOG.md) para o histórico de mudanças.

## Fontes de dados

### TACO — Tabela Brasileira de Composição de Alimentos

Banco de dados desenvolvido pelo Núcleo de Estudos e Pesquisas em Alimentação
(NEPA) da UNICAMP, com informações sobre a composição nutricional de centenas de
alimentos consumidos no Brasil, amostrados em distintas regiões do país. É
amplamente utilizada por nutricionistas, pesquisadores, profissionais da saúde e
pela indústria alimentícia.

- [Tabela TACO (XLS)](https://www.nepa.unicamp.br/taco/contar/Taco_4a_edicao_2011.xls?arquivo=1)
- [Tabela TACO (PDF)](https://www.nepa.unicamp.br/taco/contar/taco_4_edicao_ampliada_e_revisada.pdf?arquivo=1)

### Guia Alimentar para a População Brasileira

Documento oficial do Ministério da Saúde (2ª edição, 2014) que orienta práticas
alimentares saudáveis, classificando os alimentos em quatro categorias segundo o
grau de processamento: **in natura ou minimamente processados**, **ingredientes
culinários**, **processados** e **ultraprocessados**.

- [Guia Alimentar (PDF)](https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf)

### POF — Pesquisa de Orçamentos Familiares (IBGE)

Pesquisa domiciliar do IBGE sobre estruturas de consumo, gastos, rendimentos e
condições de vida das famílias brasileiras. Este repositório inclui a **Tabela de
Medidas Referidas** (POF 2008–2009), que associa medidas caseiras ("colher de
sopa", "copo", "fatia") a quantidades em gramas ou mililitros.

- [Página oficial da POF](https://www.ibge.gov.br/estatisticas/sociais/populacao/9050-pesquisa-de-orcamentos-familiares.html?edicao=9064&t=resultados)
- [Tabela de Medidas Referidas (ZIP)](https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2008_2009/Tabela_de_Medidas_Referidas_para_os_Alimentos_Consumidos_no_Brasil/tabelamedidas.zip)
- [Tabela de Medidas Referidas — Banco de Dados (ZIP)](https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2008_2009/Tabela_de_Medidas_Referidas_para_os_Alimentos_Consumidos_no_Brasil/tabelamedidas_bd.zip)

## Como citar

```bibtex
@misc{brolesi2026taco,
  author       = {Brolesi, F. F.},
  title        = {{TACO} - Tabela Brasileira de Composição de Alimentos: Repositório para acesso facilitado aos dados da {TACO} ({NEPA/UNICAMP}) e {POF} ({IBGE})},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/brolesi/taco},
  note         = {Acessado em: [data de acesso]}
}
```

**Importante:** este repositório reorganiza dados públicos. Para trabalhos
acadêmicos, cite também as fontes primárias:

- NEPA/UNICAMP. *Tabela Brasileira de Composição de Alimentos (TACO)*. 4ª ed. Campinas, 2011.
- IBGE. *Pesquisa de Orçamentos Familiares 2008-2009: Tabela de Medidas Referidas para os Alimentos Consumidos no Brasil*. Rio de Janeiro, 2011.
- BRASIL. Ministério da Saúde. *Guia Alimentar para a População Brasileira*. 2ª ed. Brasília, 2014.

## Licença

O **código** deste repositório está licenciado sob a [licença MIT](LICENSE).
Os **dados** pertencem às respectivas fontes (NEPA/UNICAMP, IBGE e Ministério da
Saúde) e são redistribuídos aqui por serem de acesso público; consulte as fontes
primárias para os termos de uso originais.

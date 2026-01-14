```

## Fontes e Referências

### TACO
- [Site oficial NEPA/UNICAMP](https://www.nepa.unicamp.br/taco/tabela.php)
- Arquivos originais: ver `originais/urls-originais.txt`

### POF
- [Site oficial IBGE](https://www.ibge.gov.br/estatisticas/sociais/populacao/9050-pesquisa-de-orcamentos-familiares.html?edicao=9064)
- [Tabela de Medidas Referidas para os Alimentos Consumidos no Brasil (PDF e XLS)](https://ftp.ibge.gov.br/Orcamentos_Familiares/Pesquisa_de_Orcamentos_Familiares_2008_2009/Tabela_de_Medidas_Referidas_para_os_Alimentos_Consumidos_no_Brasil/)

## Licença
Este repositório apenas reorganiza e facilita o acesso a dados públicos do NEPA/UNICAMP e IBGE. Consulte as licenças e termos de uso originais para cada fonte.

---
Colabore! Sugestões, issues e pull requests são bem-vindos.

## Como Usar

### Em R
```r
alimentos <- read.csv('formatados/alimentos.csv', encoding = 'UTF-8')
head(alimentos)
```

### Em Python (pandas)
```python
import pandas as pd
alimentos = pd.read_csv('formatados/alimentos.csv', encoding='utf-8')
print(alimentos.head())
```

# TACO - Tabela Brasileira de Composição de Alimentos

> **Repositório para acesso facilitado, análise e integração dos dados da TACO (NEPA/UNICAMP) e POF (IBGE) em formatos prontos para uso em ciência de dados, nutrição e saúde pública.**

## Visão Geral
Este repositório reúne arquivos originais e versões processadas das principais tabelas brasileiras de composição de alimentos, facilitando o uso em projetos de análise nutricional, scripts em R/Python, e integração com bancos de dados.

## Estrutura do Repositório


```
├── formatados/   # Tabelas em CSV prontas para análise (R, Python, etc.)
│   ├── alimentos.csv
│   ├── aminoacidos.csv
│   └── acidos-graxos.csv
├── originais/    # Arquivos originais (XLS, PDF, fontes)
│   ├── Taco_4a_edicao_2011.xls
│   ├── taco_4_edicao_ampliada_e_revisada.pdf
│   ├── guia_alimentar_populacao_brasileira_2ed.pdf
│   └── urls-originais.txt
├── tabelas/      # CSVs semi-estruturados (pré-processamento)
│   ├── alimentos.csv
│   ├── aminoacidos.csv
│   └── acidos-graxos.csv
├── pof/          # Dados da Pesquisa de Orçamentos Familiares (IBGE)
│   ├── tabelamedidas.xls
│   └── tabelamedidas_bd.xls
└── README.md
```

## Conteúdo dos Dados

### TACO (NEPA/UNICAMP)
- **Fonte:** [NEPA/UNICAMP - TACO](https://www.nepa.unicamp.br/taco/tabela.php)
- **Arquivos originais:** disponíveis em `originais/` (XLS, PDF)
- **Arquivos processados:**
	- `formatados/`: CSVs prontos para análise, com nomes de colunas padronizados e dados limpos
	- `tabelas/`: CSVs semi-estruturados, extraídos dos originais

#### Exemplos de tabelas disponíveis:
- **alimentos.csv:** Informações nutricionais gerais (energia, proteínas, lipídeos, carboidratos, fibras, minerais, vitaminas)
- **aminoacidos.csv:** Perfil de aminoácidos dos alimentos
- **acidos-graxos.csv:** Perfil de ácidos graxos dos alimentos

### POF (IBGE)
- **Fonte:** [Pesquisa de Orçamentos Familiares - IBGE](https://www.ibge.gov.br/estatisticas/sociais/populacao/9050-pesquisa-de-orcamentos-familiares.html?edicao=9064)
- **Arquivos:** disponíveis em `pof/` (tabelas de medidas referidas, microdados)

# POF - Pesquisa de Orçamentos Familiares

https://www.ibge.gov.br/estatisticas/sociais/populacao/9050-pesquisa-de-orcamentos-familiares.html?edicao=9064

https://www.ibge.gov.br/estatisticas/sociais/populacao/9050-pesquisa-de-orcamentos-familiares.html?edicao=9064&t=resultados

Sobre - Tabela de medidas referidas para os alimentos consumidos no Brasil
A Pesquisa de Orçamentos Familiares 2008-2009 teve por objetivo fornecer informações sobre a composição dos orçamentos domésticos, a partir da investigação dos hábitos de consumo, da alocação de gastos e da distribuição dos rendimentos, segundo as características dos domicílios e das pessoas. A POF investigou, também, a autopercepção da qualidade de vida e as características do perfil nutricional da população brasileira.

Dando prosseguimento à divulgação de resultados da pesquisa, o IBGE apresenta, nesta publicação, a Tabela de Medidas Referidas para os Alimentos Consumidos no Brasil, na qual é identificada, para cada tipo de produto e forma de preparação, a quantidade em gramas ou mililitros associada à medida citada para servi-lo. Para sua construção, foram compilados os dados relatados pelos informantes sobre a ingestão dos diferentes alimentos consumidos no domicílio ou fora dele, nas áreas urbana e rural de todo o País, e utilizadas outras fontes de consulta, como publicações técnico-científicas, rótulos de alimentos e pesagens diretas realizadas em centros de pesquisas de universidades brasileiras. O estudo foi realizado em parceria com o Ministério da Saúde. Para a avaliação, compilação e estruturação dos resultados ora apresentados, o IBGE contou com a contribuição de técnicos do Órgão parceiro e, também, com especialistas em nutrição, de reconhecida experiência e competência, mobilizados por aquele Ministério.

A publicação inclui, ainda, uma visão dos objetivos da pesquisa e da metodologia utilizada, com ênfase nos principais conceitos e definições, aspectos de amostragem, instrumentos e procedimentos de coleta e tratamento das informações. O CD-ROM que a acompanha reproduz o presente volume e contém uma planilha complementar, com as informações constantes na tabela impressa, o que permite ao usuário o cruzamento de dados bem como a construção de outras planilhas segundo sua perspectiva de interesse. Apresenta, adicionalmente, os dois instrumentos utilizados durante a etapa de coleta das informações sobre o consumo alimentar pessoal: o Bloco de Consumo Alimentar Pessoal, POF 7, utilizado pelos informantes para a anotação dos registros de ingestão alimentar, e as respectivas Instruções para o Preenchimento.

O IBGE disponibiliza também os microdados da pesquisa para facilitar a exploração de sua base de dados segundo a perspectiva de interesse dos usuários.  
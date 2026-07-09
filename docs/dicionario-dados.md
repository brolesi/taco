# Dicionário de Dados — CSVs processados da TACO

Os arquivos em [`data/processed/taco/`](../data/processed/taco/) são gerados por
[`scripts/process_taco.py`](../scripts/process_taco.py) a partir da planilha original
`data/raw/taco/Taco_4a_edicao_2011.xls` (TACO, 4ª edição, NEPA/UNICAMP).

Todos os valores nutricionais referem-se a **100 g de parte comestível** do alimento.

## Valores especiais

| Valor no CSV | Origem na planilha | Significado |
|---|---|---|
| `1e-05` | `Tr` | Traço: quantidade abaixo do limite de quantificação |
| vazio (NaN) | vazio ou `NA` | Não analisado / não aplicável |

A coluna `categoria` é derivada das **linhas separadoras** presentes nas abas da
planilha original (os alimentos não estão numerados em faixas contíguas por
categoria). Na aba de aminoácidos, que não possui separadores, a categoria é
obtida pelo `numero_alimento` a partir da aba de composição. As 15 categorias,
com os rótulos exatos da publicação:

| Categoria | Alimentos (composição) |
|---|---|
| Alimentos preparados | 32 |
| Bebidas (alcoólicas e não alcoólicas) | 14 |
| Carnes e derivados | 123 |
| Cereais e derivados | 63 |
| Frutas e derivados | 96 |
| Gorduras e óleos | 14 |
| Leguminosas e derivados | 30 |
| Leite e derivados | 24 |
| Miscelâneas | 9 |
| Nozes e sementes | 11 |
| Outros alimentos industrializados | 5 |
| Ovos e derivados | 7 |
| Pescados e frutos do mar | 50 |
| Produtos açucarados | 20 |
| Verduras, hortaliças e derivados | 99 |

## `taco_composicao.csv` (597 alimentos)

Composição centesimal, minerais e vitaminas. A coluna "Campo na API" indica o nome
exposto pela API REST.

| Coluna | Unidade | Descrição | Campo na API |
|---|---|---|---|
| `numero_alimento` | — | Identificador do alimento na TACO | `id` |
| `descricao` | — | Descrição do alimento | `description` |
| `categoria` | — | Categoria do alimento | `category` |
| `umidade_pct` | % | Umidade | `moisture_pct` |
| `energia_kcal` | kcal | Energia | `energy_kcal` |
| `energia_kj` | kJ | Energia | `energy_kj` |
| `proteina_g` | g | Proteína | `protein_g` |
| `lipideos_g` | g | Lipídeos totais | `lipids_g` |
| `colesterol_mg` | mg | Colesterol | `cholesterol_mg` |
| `carboidrato_g` | g | Carboidrato total | `carbohydrate_g` |
| `fibra_g` | g | Fibra alimentar | `dietary_fiber_g` |
| `cinzas_g` | g | Cinzas (resíduo mineral) | `ash_g` |
| `calcio_mg` | mg | Cálcio | `calcium_mg` |
| `magnesio_mg` | mg | Magnésio | `magnesium_mg` |
| `manganes_mg` | mg | Manganês | `manganese_mg` |
| `fosforo_mg` | mg | Fósforo | `phosphorus_mg` |
| `ferro_mg` | mg | Ferro | `iron_mg` |
| `sodio_mg` | mg | Sódio | `sodium_mg` |
| `potassio_mg` | mg | Potássio | `potassium_mg` |
| `cobre_mg` | mg | Cobre | `copper_mg` |
| `zinco_mg` | mg | Zinco | `zinc_mg` |
| `retinol_mcg` | µg | Retinol | `retinol_mcg` |
| `RE_mcg` | µg | Equivalente de retinol (RE) | `re_mcg` |
| `RAE_mcg` | µg | Equivalente de atividade de retinol (RAE) | `rae_mcg` |
| `tiamina_mg` | mg | Tiamina (vitamina B1) | `thiamine_mg` |
| `riboflavina_mg` | mg | Riboflavina (vitamina B2) | `riboflavin_mg` |
| `piridoxina_mg` | mg | Piridoxina (vitamina B6) | `pyridoxine_mg` |
| `niacina_mg` | mg | Niacina (vitamina B3) | `niacin_mg` |
| `vitamina_c_mg` | mg | Vitamina C | `vitamin_c_mg` |

## `taco_acidos_graxos.csv` (423 alimentos)

Perfil de ácidos graxos. Notação `cX_Y`: cadeia com X carbonos e Y insaturações.

| Coluna | Unidade | Descrição | Campo na API |
|---|---|---|---|
| `numero_alimento` | — | Identificador do alimento | `id` |
| `descricao` | — | Descrição do alimento | `description` |
| `categoria` | — | Categoria do alimento | `category` |
| `saturados_g` | g | Ácidos graxos saturados totais | `saturated_g` |
| `monoinsaturados_g` | g | Monoinsaturados totais | `monounsaturated_g` |
| `poliinsaturados_g` | g | Poli-insaturados totais | `polyunsaturated_g` |
| `c12_0_g` | g | Láurico (12:0) | `c12_0_g` |
| `c14_0_g` | g | Mirístico (14:0) | `c14_0_g` |
| `c16_0_g` | g | Palmítico (16:0) | `c16_0_g` |
| `c18_0_g` | g | Esteárico (18:0) | `c18_0_g` |
| `c20_0_g` | g | Araquídico (20:0) | `c20_0_g` |
| `c22_0_g` | g | Beênico (22:0) | `c22_0_g` |
| `c24_0_g` | g | Lignocérico (24:0) | `c24_0_g` |
| `c14_1_g` | g | Miristoleico (14:1) | `c14_1_g` |
| `c16_1_g` | g | Palmitoleico (16:1) | `c16_1_g` |
| `c18_1_g` | g | Oleico (18:1) | `c18_1_g` |
| `c20_1_g` | g | Gadoleico (20:1) | `c20_1_g` |
| `c18_2n6_g` | g | Linoleico (18:2 n-6) | `c18_2_n6_g` |
| `c18_3n3_g` | g | Alfa-linolênico (18:3 n-3) | `c18_3_n3_g` |
| `c20_4_g` | g | Araquidônico (20:4) | `c20_4_g` |
| `c20_5_g` | g | EPA (20:5) | `epa_c20_5_g` |
| `c22_5_g` | g | DPA (22:5) | `dpa_c22_5_g` |
| `c22_6_g` | g | DHA (22:6) | `dha_c22_6_g` |
| `c18_1t_g` | g | Trans-oleico (18:1t) | `trans_c18_1_g` |
| `c18_2t_g` | g | Trans-linoleico (18:2t) | `trans_c18_2_g` |

## `taco_aminoacidos.csv` (26 alimentos)

Perfil de aminoácidos, disponível apenas para um subconjunto de alimentos.

| Coluna | Unidade | Descrição | Campo na API |
|---|---|---|---|
| `numero_alimento` | — | Identificador do alimento | `id` |
| `descricao` | — | Descrição do alimento | `description` |
| `categoria` | — | Categoria do alimento | `category` |
| `triptofano_g` | g | Triptofano | `tryptophan_g` |
| `treonina_g` | g | Treonina | `threonine_g` |
| `isoleucina_g` | g | Isoleucina | `isoleucine_g` |
| `leucina_g` | g | Leucina | `leucine_g` |
| `lisina_g` | g | Lisina | `lysine_g` |
| `metionina_g` | g | Metionina | `methionine_g` |
| `cistina_g` | g | Cistina | `cystine_g` |
| `fenilalanina_g` | g | Fenilalanina | `phenylalanine_g` |
| `tirosina_g` | g | Tirosina | `tyrosine_g` |
| `valina_g` | g | Valina | `valine_g` |
| `arginina_g` | g | Arginina | `arginine_g` |
| `histidina_g` | g | Histidina | `histidine_g` |
| `alanina_g` | g | Alanina | `alanine_g` |
| `acido_aspartico_g` | g | Ácido aspártico | `aspartic_acid_g` |
| `acido_glutamico_g` | g | Ácido glutâmico | `glutamic_acid_g` |
| `glicina_g` | g | Glicina | `glycine_g` |
| `prolina_g` | g | Prolina | `proline_g` |
| `serina_g` | g | Serina | `serine_g` |

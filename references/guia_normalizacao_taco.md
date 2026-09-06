# Guia de Normalização - Planilha TACO 4ª Edição

## Estrutura da Planilha

A planilha contém **3 abas**:

| Aba | Descrição | Linhas | Colunas |
|-----|-----------|--------|---------|
| CMVCol taco3 | Composição nutricional principal | 696 | 29 |
| AGtaco3 | Ácidos graxos | 494 | 25 |
| Aminoácidos TACO3 | Perfil de aminoácidos | 29 | 21 |

---

## Aba 1: CMVCol taco3 (Composição Nutricional)

### Estrutura Atual

- **Linhas 0-2**: Cabeçalho em 3 níveis (mesclado)
- **Linhas de categoria**: Separadores como "Cereais e derivados" (sem dados numéricos)
- **Linhas de dados**: Alimentos com valores nutricionais
- **Linhas 688-695**: Legendas e notas de rodapé

### Operações de Normalização

```python
import pandas as pd

# 1. Carregar ignorando as primeiras linhas
df = pd.read_excel("arquivo.xlsx", sheet_name="CMVCol taco3", header=None)

# 2. Definir cabeçalho manualmente (unificar as 3 linhas)
colunas = [
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
]

# 3. Remover linhas de cabeçalho original (0-2)
df = df.iloc[3:]

# 4. Aplicar nomes de colunas
df.columns = colunas

# 5. Identificar e remover linhas de categoria
# São linhas onde a coluna 'descricao' está vazia ou todas as colunas numéricas são NaN
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

# 6. Remover linhas de legenda/rodapé (caracteres especiais)
df = df[~df["numero_alimento"].astype(str).str.match(r"^[†\*]")]
df = df[df["numero_alimento"].notna()]

# 7. Converter 'numero_alimento' para inteiro (remover linhas inválidas)
df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
df["numero_alimento"] = df["numero_alimento"].astype(int)

# 8. Tratar valores especiais
# 'Tr' = traço (valor muito pequeno, < limite de quantificação) → substituir por 0 ou manter como texto
# Se quiser substituir por 0:
df = df.replace("Tr", 0)

# 9. Remover coluna duplicada 'numero_alimento_2'
df = df.drop(columns=["numero_alimento_2"])

# 10. Converter colunas numéricas
colunas_numericas = df.columns.drop(["numero_alimento", "descricao"])
for col in colunas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 11. Exportar
df.to_csv("taco_composicao.csv", index=False, encoding="utf-8")
```

### Decisões a Tomar

| Questão | Opções |
|---------|--------|
| O que fazer com "Tr" (traço)? | `0`, `NaN`, ou manter como texto |
| Adicionar coluna de categoria? | Criar coluna `categoria` baseada na posição |
| Manter coluna duplicada? | `numero_alimento_2` é redundante |

---

## Aba 2: AGtaco3 (Ácidos Graxos)

### Estrutura Atual

- **Linhas 0-2**: Cabeçalho em 3 níveis
- **Linhas de categoria**: Mesmas categorias da aba principal
- **Linhas de dados**: Perfil de ácidos graxos por alimento

### Operações de Normalização

```python
df = pd.read_excel("arquivo.xlsx", sheet_name="AGtaco3", header=None)

# Cabeçalho unificado
colunas = [
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
]

# Aplicar mesma lógica de limpeza da aba 1
df = df.iloc[3:]
df.columns = colunas

# Remover categorias e legendas
df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
df["numero_alimento"] = df["numero_alimento"].astype(int)

# Tratar 'Tr' e remover coluna duplicada
df = df.replace("Tr", 0)
df = df.drop(columns=["numero_alimento_2"])

# Converter e exportar
colunas_numericas = df.columns.drop(["numero_alimento", "descricao"])
for col in colunas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_csv("taco_acidos_graxos.csv", index=False, encoding="utf-8")
```

---

## Aba 3: Aminoácidos TACO3

### Estrutura Atual

- **Linhas 0-2**: Cabeçalho em 3 níveis
- **Linhas 3-28**: Dados (apenas 26 alimentos)
- **Sem linhas de categoria**

### Operações de Normalização

```python
df = pd.read_excel("arquivo.xlsx", sheet_name="Aminoácidos TACO3", header=None)

colunas = [
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
]

df = df.iloc[3:]
df.columns = colunas

df = df[pd.to_numeric(df["numero_alimento"], errors="coerce").notna()]
df["numero_alimento"] = df["numero_alimento"].astype(int)
df = df.drop(columns=["numero_alimento_2"])

colunas_numericas = df.columns.drop(["numero_alimento", "descricao"])
for col in colunas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_csv("taco_aminoacidos.csv", index=False, encoding="utf-8")
```

---

## Resumo das Operações

| Operação | CMVCol | AGtaco3 | Aminoácidos |
|----------|--------|---------|-------------|
| Remover linhas 0-2 (cabeçalho fragmentado) | ✓ | ✓ | ✓ |
| Definir cabeçalho unificado | ✓ | ✓ | ✓ |
| Remover linhas de categoria | ✓ | ✓ | — |
| Remover linhas de legenda/rodapé | ✓ | ✓ | — |
| Tratar valor "Tr" | ✓ | ✓ | — |
| Remover coluna duplicada | ✓ | ✓ | ✓ |
| Converter tipos numéricos | ✓ | ✓ | ✓ |

---

## Adicionar Coluna de Categoria

A categoria deve ser derivada das **linhas separadoras** da própria aba, com
forward-fill, **antes** de removê-las.

> ⚠️ Não use faixas de `numero_alimento` para inferir a categoria: a numeração
> **não** é contígua por categoria (ex.: o alimento 561, "Feijão, carioca,
> cozido", pertence a "Leguminosas e derivados", não a uma faixa de "Produtos
> açucarados").

```python
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
]

# Antes de filtrar as linhas separadoras:
rotulos = df["numero_alimento"]
df["categoria"] = rotulos.where(rotulos.isin(categorias)).ffill()

# ... em seguida, aplicar o filtro que mantém apenas linhas de dados.
```

Para a aba de aminoácidos (sem linhas separadoras), obtenha a categoria pelo
`numero_alimento`, cruzando com a aba de composição já processada.

---

## Valores Especiais

| Valor | Significado | Recomendação |
|-------|-------------|--------------|
| `Tr` | Traço (< limite quantificação) | Substituir por `0` ou `NaN` |
| `NaN` / vazio | Não analisado | Manter como `NaN` |
| `NA` | Não aplicável | Manter como `NaN` |

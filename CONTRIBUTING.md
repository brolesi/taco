# Contribuindo

Obrigado pelo interesse em contribuir! Este guia descreve o fluxo básico.

## Configuração do ambiente

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements-dev.txt
```

## Fluxo de trabalho

1. Crie um branch a partir de `main` (`git checkout -b minha-mudanca`).
2. Faça as alterações. Se mudar o pipeline, regenere os CSVs com
   `python scripts/process_taco.py` e inclua-os no commit.
3. Rode o lint e os testes antes de abrir o PR:

   ```bash
   ruff check .
   pytest
   ```

4. Abra um Pull Request descrevendo a motivação da mudança.

## Padrões

- **Estilo de código:** [Ruff](https://docs.astral.sh/ruff/) com linha de até
  100 caracteres (configurado em `pyproject.toml`). O CI falha se o lint não passar.
- **Dados:** os arquivos em `data/raw/` são imutáveis (fontes originais);
  os de `data/processed/` devem ser sempre reproduzíveis pelo pipeline.
  Não edite CSVs processados manualmente.
- **API:** mudanças de contrato (nomes de campos, rotas) devem ser registradas
  no [CHANGELOG.md](CHANGELOG.md) e refletidas em
  [docs/dicionario-dados.md](docs/dicionario-dados.md).
- **Commits:** mensagens curtas no imperativo, descrevendo o "porquê" quando
  não for óbvio.

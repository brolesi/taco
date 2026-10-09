# API TACO pronta para uso: docker build -t taco . && docker run -p 8000:8000 taco
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Só o que a API lê: o código e os CSVs processados (versionados no repositório).
COPY api/ api/
COPY data/processed/ data/processed/

USER nobody
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

@echo off
rem Sobe a API TACO em modo de desenvolvimento (http://127.0.0.1:8000).
rem Ativa o ambiente virtual .venv, se existir.
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
python -m uvicorn api.main:app --reload

@echo off
echo ==========================================
echo    PREPARANDO AMBIENTE (AGUARDE...)
echo ==========================================

:: 1. Instala/Verifica as bibliotecas automaticamente
pip install -r requirements.txt

:: Limpa a tela para ficar bonito
cls

echo ==========================================
echo    INICIANDO AUTOMACAO DE PDFs
echo ==========================================

:: 2. Roda o programa principal
python src/main.py

echo.
echo ==========================================
echo    FIM DO PROCESSO
echo ==========================================
pause
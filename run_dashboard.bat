@echo off
title Dashboard Financeiro

echo Iniciando o Dashboard Financeiro...
echo Uma nova aba abrira automaticamente no seu navegador em alguns instantes.
echo.
echo IMPORTANTE: Esta janela do terminal precisa permanecer aberta para que o dashboard funcione.
echo Para encerrar, basta fechar esta janela.
echo.

REM Navega para o diretorio do projeto
cd /d "E:\Nandho\Finanças\dashboard-financeiro"

REM Executa o dashboard do Streamlit
streamlit run dashboard.py 
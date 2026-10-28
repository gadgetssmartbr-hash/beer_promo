@echo off
title Bot de Promocoes de Bebidas e Vinhos - Sertaozinho
chcp 65001 > nul
cd /d "%~dp0"
echo ===================================================
echo   INICIANDO BOT DE PROMOCOES E SOMMELIER DE VINHOS
echo ===================================================
echo.
python bot.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] O bot encerrou com codigo de erro %ERRORLEVEL%.
    pause
)

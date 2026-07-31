@echo off
title Build - IP Scanner Pro
echo ============================================
echo   IP Scanner Pro - Build
echo ============================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH!
    pause
    exit /b 1
)
echo.

echo [2/4] Instalando dependencias...
pip install pyinstaller customtkinter requests urllib3 reportlab certifi --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo      OK
echo.

echo [3/4] Limpando builds anteriores...
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
echo      OK
echo.

echo [4/4] Compilando executavel...
echo      (isso pode levar 1-3 minutos)
echo.
pyinstaller ip_scanner.spec --noconfirm --clean
echo.

if exist "dist\IP Scanner Pro\IP Scanner Pro.exe" (
    echo ============================================
    echo   BUILD CONCLUIDO COM SUCESSO!
    echo.
    echo   Executavel em:
    echo   dist\IP Scanner Pro\IP Scanner Pro.exe
    echo ============================================
    echo.
    echo Copiando pasta config para dist...
    if exist "config" xcopy /E /I /Y "config" "dist\IP Scanner Pro\config" >nul 2>nul
    echo.
    echo Abrindo pasta de saida...
    explorer "dist\IP Scanner Pro"
) else (
    echo ============================================
    echo   ERRO NO BUILD!
    echo.
    echo   Verifique:
    echo   1. Os arquivos estao na estrutura correta?
    echo   2. Todas as dependencias estao instaladas?
    echo   3. O ip_scanner.spec esta na raiz do projeto?
    echo ============================================
)

echo.
pause

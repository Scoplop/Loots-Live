@echo off
REM Script d'arrêt du serveur - Loots&Live
echo ================================================
echo Arret du serveur Loots^&Live
echo ================================================
echo.

echo Recherche du processus uvicorn...

REM Trouver et tuer le processus uvicorn
for /f "tokens=2" %%a in ('tasklist ^| findstr /i "uvicorn"') do (
    echo Arret du processus %%a...
    taskkill /F /PID %%a >nul 2>&1
)

REM Vérifier si d'autres processus Python liés au serveur existent
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Arret du processus utilisant le port 8000 (PID: %%a^)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ================================================
echo Serveur arrete !
echo ================================================
pause

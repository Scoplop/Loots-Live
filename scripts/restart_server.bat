@echo off
REM Script de redémarrage du serveur - Loots&Live
echo ================================================
echo Redemarrage du serveur Loots^&Live
echo ================================================
echo.

echo Arret du serveur actuel...
call stop_server.bat

timeout /t 2 /nobreak >nul

echo.
echo Redemarrage du serveur...
call start_server.bat

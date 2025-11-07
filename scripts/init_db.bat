@echo off
REM Script d'initialisation de la base de données - Loots&Live
echo ================================================
echo Initialisation de la base de donnees
echo ================================================
echo.

REM Vérifier si le venv existe
if not exist venv (
    echo ERREUR: L'environnement virtuel n'existe pas
    echo Veuillez lancer install_dependencies.bat d'abord
    pause
    exit /b 1
)

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Initialisation de la base de donnees...
python backend\scripts\init_db.py

if errorlevel 1 (
    echo ERREUR: Echec de l'initialisation
    pause
    exit /b 1
)

echo.
echo ================================================
echo Base de donnees initialisee avec succes !
echo ================================================
pause

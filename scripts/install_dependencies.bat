@echo off
REM Script d'installation des dépendances - Loots&Live
echo ================================================
echo Installation des dependances Loots^&Live
echo ================================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Veuillez installer Python 3.10+ depuis python.org
    pause
    exit /b 1
)

echo [1/4] Verification de la version Python...
python --version

echo.
echo [2/4] Creation de l'environnement virtuel...
if exist venv (
    echo L'environnement virtuel existe deja, on le supprime...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERREUR: Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)

echo.
echo [3/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo [4/4] Installation des dependances...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR: Impossible d'installer les dependances
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installation terminee avec succes !
echo ================================================
echo.
echo Prochaines etapes :
echo 1. Copiez .env.example vers .env et ajustez les valeurs
echo 2. Lancez init_db.bat pour initialiser la base de donnees
echo 3. Lancez start_server.bat pour demarrer l'application
echo.
pause

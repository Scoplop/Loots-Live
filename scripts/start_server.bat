@echo off
REM Script de démarrage du serveur - Loots&Live
echo ================================================
echo Demarrage du serveur Loots^&Live
echo ================================================
echo.

REM Vérifier si le venv existe
if not exist venv (
    echo ERREUR: L'environnement virtuel n'existe pas
    echo Veuillez lancer install_dependencies.bat d'abord
    pause
    exit /b 1
)

REM Vérifier si .env existe
if not exist .env (
    echo ATTENTION: Le fichier .env n'existe pas
    echo Copie de .env.example vers .env...
    copy .env.example .env
    echo.
    echo IMPORTANT: Editez le fichier .env pour configurer l'application
    echo Appuyez sur une touche pour continuer quand meme...
    pause
)

REM Vérifier si la DB existe
if not exist data\lootsandlive.db (
    echo ATTENTION: La base de donnees n'existe pas
    echo Initialisation de la base de donnees...
    call venv\Scripts\activate.bat
    python backend\scripts\init_db.py
    if errorlevel 1 (
        echo ERREUR: Impossible d'initialiser la base de donnees
        pause
        exit /b 1
    )
)

REM Vérifier si Ollama est en cours d'exécution
echo Verification de la disponibilite d'Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo.
    echo ATTENTION: Ollama ne semble pas accessible sur localhost:11434
    echo L'IA ne fonctionnera pas correctement sans Ollama
    echo.
    echo Pour installer Ollama : https://ollama.ai
    echo Pour demarrer Ollama : ollama serve
    echo.
    echo Voulez-vous continuer quand meme ? (O/N^)
    choice /C ON /M "Continuer"
    if errorlevel 2 exit /b 0
)

echo.
echo [1/2] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo [2/2] Demarrage du serveur FastAPI sur http://127.0.0.1:8000 ...
echo.
echo ================================================
echo Serveur demarre !
echo ================================================
echo.
echo Interface web : http://127.0.0.1:8000
echo Documentation API : http://127.0.0.1:8000/docs
echo.
echo Appuyez sur CTRL+C pour arreter le serveur
echo.

uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

REM Si le serveur s'arrête
echo.
echo Serveur arrete.
pause

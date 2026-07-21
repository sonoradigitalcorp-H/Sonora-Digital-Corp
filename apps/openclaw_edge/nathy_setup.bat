@echo off
title Instalador Nathy Edge Client
echo ============================================
echo  Nathy Conta — Edge Client para Windows
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Descargalo de: https://python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado

:: Crear estructura de carpetas
echo.
echo Creando estructura en C:\NathyConta...
mkdir "C:\NathyConta\Inbox" 2>nul
mkdir "C:\NathyConta\Clientes" 2>nul
mkdir "C:\NathyConta\Procesados" 2>nul
mkdir "C:\NathyConta\Errores" 2>nul
mkdir "C:\NathyConta\Pendientes" 2>nul
mkdir "C:\NathyConta\Duplicados" 2>nul
mkdir "C:\NathyConta\Logs" 2>nul
mkdir "C:\NathyConta\Config" 2>nul
echo [OK] Carpetas creadas

:: Copiar config si no existe
if not exist "C:\NathyConta\Config\config.yaml" (
    copy nathy_config.yaml "C:\NathyConta\Config\config.yaml" >nul
    echo [OK] Configuracion creada
    echo IMPORTANTE: Edita C:\NathyConta\Config\config.yaml con tu API key
)

:: Instalar dependencias
echo.
echo Instalando dependencias...
pip install watchdog httpx pyyaml win10toast --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

:: Crear acceso directo en startup
echo.
echo Creando acceso en Inicio...
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $sc = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Nathy Edge.lnk'); ^
     $sc.TargetPath = 'python'; ^
     $sc.Arguments = '%~dp0nathy_edge_client.py'; ^
     $sc.WorkingDirectory = '%~dp0'; ^
     $sc.Save()"
echo [OK] Acceso creado — se iniciara automaticamente al encender

:: Probar inicio
echo.
echo Iniciando cliente...
start /B python nathy_edge_client.py

echo.
echo ============================================
echo  INSTALACION COMPLETA
echo ============================================
echo.
echo  Pasos siguientes:
echo  1. Edita C:\NathyConta\Config\config.yaml
echo     con tu API key (te la dara el sistema)
echo  2. Arrastra tus XMLs/PDFs a C:\NathyConta\Inbox\
echo  3. El cliente los organiza automaticamente
echo.
echo  Para ver el log: C:\NathyConta\Logs\nathy-edge.log
echo.
pause

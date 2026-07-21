@echo off
REM ============================================================
REM OpenClaw Edge — Instalador Windows para Nathaly (Fourgea)
REM ============================================================
echo.
echo ========================================
echo   OpenClaw Edge — Fourgea Mexico
echo   Instalador para Laptop Nathaly
echo ========================================
echo.

REM 1. Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde python.org
    echo          Marca "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)
echo [OK] Python detectado
python --version

REM 2. Crear estructura de carpetas
echo.
echo Creando C:\OpenClaw...
mkdir C:\OpenClaw\Inbox 2>nul
mkdir C:\OpenClaw\Procesados 2>nul
mkdir C:\OpenClaw\Pendientes 2>nul
mkdir C:\OpenClaw\Errores 2>nul
mkdir C:\OpenClaw\Exportaciones 2>nul
mkdir C:\OpenClaw\Logs 2>nul
echo [OK] Carpetas creadas en C:\OpenClaw

REM 3. Copiar archivos del edge client
echo.
echo Copiando archivos del edge client...
copy /Y edge_client.py C:\OpenClaw\ >nul
copy /Y config.example.yaml C:\OpenClaw\config.yaml >nul
copy /Y requirements.txt C:\OpenClaw\ >nul
echo [OK] Archivos copiados

REM 4. Instalar dependencias
echo.
echo Instalando dependencias Python...
pip install -r C:\OpenClaw\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo instalacion de dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

REM 5. Crear acceso directo en el Escritorio
echo.
echo Creando acceso directo en Escritorio...
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $s = $ws.CreateShortcut($ws.SpecialFolders('Desktop') + '\OpenClaw Edge.lnk'); ^
     $s.TargetPath = 'pythonw.exe'; ^
     $s.Arguments = 'C:\OpenClaw\edge_client.py --config C:\OpenClaw\config.yaml'; ^
     $s.WorkingDirectory = 'C:\OpenClaw'; ^
     $s.IconLocation = 'C:\Windows\System32\imageres.dll,14'; ^
     $s.Save()"
echo [OK] Acceso directo creado

echo.
echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo  IMPORTANTE: Edita C:\OpenClaw\config.yaml
echo  y coloca la API key REAL en vps.api_key
echo.
echo  Para iniciar: Doble clic en el acceso directo
echo                 "OpenClaw Edge" en el Escritorio
echo.
echo  Carpetas:
echo    C:\OpenClaw\Inbox       <- Aqui se guardan los adjuntos
echo    C:\OpenClaw\Procesados  <- Archivos procesados correctamente
echo    C:\OpenClaw\Errores     <- Archivos con errores
echo    C:\OpenClaw\Logs        <- Registro de actividad
echo.
pause

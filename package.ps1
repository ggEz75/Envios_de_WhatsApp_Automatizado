# package.ps1
# Script de empaquetado para Windows usando PyInstaller.
# Uso: Ejecutar desde PowerShell en la carpeta del proyecto.
#   .\package.ps1

param(
    [switch]$InstallRequirements
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

if ($InstallRequirements) {
    Write-Host "Creando virtualenv .venv y instalando dependencias..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip
    if (Test-Path requirements.txt) {
        pip install -r requirements.txt
    }
}

# Nombre del script principal
$MainScript = "frontend.py"
$Icon = "icono.ico"

# Archivos adicionales a incluir
$AddData = @()
# coords.json puede residir en la carpeta del proyecto; se incluirá para la primera ejecución
if (Test-Path "coords.json") {
    # PyInstaller syntax on Windows: "src;dest"
    $AddData += "coords.json;."
}
if (Test-Path $Icon) {
    $AddData += "$Icon;."
}

# Construir la cadena --add-data
$AddDataArgs = ""
foreach ($d in $AddData) {
    $AddDataArgs += " --add-data `"$d`""
}

# Comando PyInstaller
$PyInstallerCmd = "pyinstaller --noconsole --onefile --clean --name EnvioWhatsApp --icon=`"$Icon`" $AddDataArgs $MainScript"
Write-Host "Ejecutando: $PyInstallerCmd"
Invoke-Expression $PyInstallerCmd

# Copiar README y requirements al dist para que el exe distribuido tenga documentación
$DistDir = Join-Path $ProjectRoot "dist"
if (Test-Path "$ProjectRoot\README.md") {
    Copy-Item "$ProjectRoot\README.md" -Destination $DistDir -Force
}
if (Test-Path "$ProjectRoot\requirements.txt") {
    Copy-Item "$ProjectRoot\requirements.txt" -Destination $DistDir -Force
}

Write-Host "Build finalizado. Revisa la carpeta 'dist' para el ejecutable y archivos adicionales."
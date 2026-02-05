# package.ps1
# Script de empaquetado para Windows usando PyInstaller.
# Uso: Ejecutar desde PowerShell en la carpeta del proyecto.
#   .\package.ps1

param(
    [switch]$InstallRequirements
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

$VenvActivated = $false
if ($InstallRequirements) {
    Write-Host "Creando virtualenv .venv y instalando dependencias..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    $VenvActivated = $true
    pip install --upgrade pip
    if (Test-Path requirements.txt) {
        pip install -r requirements.txt
    }
    pip install pyinstaller
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activando venv existente..."
    .\.venv\Scripts\Activate.ps1
    $VenvActivated = $true
}

# Nombre del script principal
$MainScript = "frontend.py"
$Icon = "icono.ico"

# Comando PyInstaller base
$PyInstallerArgs = @(
    "--noconsole",
    "--onefile",
    "--clean",
    "--name", "EnvioWhatsApp"
)

# Agregar icono si existe
if (Test-Path $Icon) {
    $PyInstallerArgs += "--icon=$Icon"
    Write-Host "Icono encontrado: $Icon"
} else {
    Write-Host "Advertencia: No se encontró icono.ico, se generará sin icono personalizado."
}

# Agregar el script principal
$PyInstallerArgs += $MainScript

# Ejecutar PyInstaller
Write-Host "Ejecutando PyInstaller..."
Write-Host "Comando: pyinstaller $($PyInstallerArgs -join ' ')"
if ($VenvActivated) {
    & pyinstaller @PyInstallerArgs
} else {
    & pyinstaller @PyInstallerArgs
}

# Copiar README y requirements al dist para que el exe distribuido tenga documentación
$DistDir = Join-Path $ProjectRoot "dist"
if (Test-Path "$ProjectRoot\README.md") {
    Copy-Item "$ProjectRoot\README.md" -Destination $DistDir -Force
}
if (Test-Path "$ProjectRoot\requirements.txt") {
    Copy-Item "$ProjectRoot\requirements.txt" -Destination $DistDir -Force
}

Write-Host "Build finalizado. Revisa la carpeta 'dist' para el ejecutable y archivos adicionales."
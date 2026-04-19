# ============================================================
#  run_local.ps1 — Script de Ejecución Local Veritasium
# ============================================================

$OPENFANG_BIN = "$HOME\.openfang\bin\openfang.exe"
$ENV_FILE = ".env"

if (-not (Test-Path $ENV_FILE)) {
    Write-Host "❌ Error: Archivo .env no encontrado." -ForegroundColor Red
    Write-Host "💡 Copia .env.example a .env y configura tus claves primero."
    exit 1
}

Write-Host "🚀 Iniciando Ecosistema-Veritasium localmente..." -ForegroundColor Cyan

# Cargar variables de entorno desde .env
Get-Content $ENV_FILE | Where-Object { $_ -match '=' -and $_ -notmatch '^#' } | ForEach-Object {
    $name, $value = $_.Split('=', 2)
    [System.Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), "Process")
}

# Verificar binario
if (-not (Test-Path $OPENFANG_BIN)) {
    Write-Host "⚠️ OpenFang no encontrado en $OPENFANG_BIN" -ForegroundColor Yellow
    Write-Host "Intentando invocar 'openfang' desde el PATH..."
    $OPENFANG_BIN = "openfang"
}

# Ejecutar OpenFang
& $OPENFANG_BIN run `
    --hand hands/recolector `
    --config config.toml `
    --state .veritasium/state.db `
    --log-dir .veritasium/logs `
    --mode $env:BOT_MODE

param (
    [string]$AgbInput
)

# Zorg dat we PowerShell 7 gebruiken indien beschikbaar
if ($PSVersionTable.PSVersion.Major -lt 7) {
    if (Get-Command pwsh -ErrorAction SilentlyContinue) {
        # Herstart dit script met pwsh
        if ($AgbInput) {
            & pwsh -NoProfile -File $PSCommandPath $AgbInput
        } else {
            & pwsh -NoProfile -File $PSCommandPath
        }
        exit $LASTEXITCODE
    } else {
        Write-Warning "PowerShell 7 (pwsh) niet gevonden. Script draait verder in versie $($PSVersionTable.PSVersion)."
    }
}

$AgbCode = $AgbInput

# 1. Als er geen input is, probeer het klembord
if ([string]::IsNullOrWhiteSpace($AgbCode)) {
    try {
        $Clipboard = Get-Clipboard
        if ($Clipboard) {
            # Pak de eerste regel als het meerdere regels zijn
            if ($Clipboard -is [array]) {
                $AgbCode = $Clipboard[0]
            } else {
                $AgbCode = $Clipboard
            }
            
            if (-not [string]::IsNullOrWhiteSpace($AgbCode)) {
                $AgbCode = $AgbCode.Trim()
                Write-Host "Gebruik klembord input: '$AgbCode'" -ForegroundColor Cyan
            }
        }
    } catch {
        # Negeer klembord errors
    }
}

# 2. Validatie
if ([string]::IsNullOrWhiteSpace($AgbCode)) {
    Write-Host "Gebruik: .\agb.ps1 [AGB-code]"
    Write-Host "Of zorg dat er een code op het klembord staat."
    exit 1
}

# Bepaal het pad naar het script
$ScriptPath = Join-Path $PSScriptRoot "agb_checker.py"

# Probeer de Python executable in de virtual environment te vinden
$VenvPath = Join-Path $PSScriptRoot ".venv"
$PythonWindows = Join-Path $VenvPath "Scripts\python.exe"

if (Test-Path $PythonWindows) {
    $PythonExe = $PythonWindows
} else {
    # Fallback naar systeem python als venv niet gevonden is
    $PythonExe = "python"
}

# Roep het Python script aan
& $PythonExe $ScriptPath $AgbCode

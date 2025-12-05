param (
    [object]$AgbInput
)

$AgbCode = $null

# 1. Check of er input is meegegeven
if ($AgbInput) {
    if ($AgbInput -is [array] -and $AgbInput.Count -gt 0) {
        $AgbCode = $AgbInput[0]
    } elseif ($AgbInput) {
        $AgbCode = $AgbInput
    }
}

# 2. Als er geen input is, probeer het klembord
if (-not $AgbCode) {
    try {
        $Clipboard = Get-Clipboard
        if ($Clipboard) {
            # Pak de eerste regel als het meerdere regels zijn
            if ($Clipboard -is [array]) {
                $AgbCode = $Clipboard[0]
            } else {
                $AgbCode = $Clipboard
            }
            
            if ($AgbCode) {
                $AgbCode = $AgbCode.Trim()
                Write-Host "Gebruik klembord input: '$AgbCode'" -ForegroundColor Cyan
            }
        }
    } catch {
        # Negeer klembord errors
    }
}

# 3. Validatie
if (-not $AgbCode) {
    Write-Host "Gebruik: agb <AGB-code>"
    Write-Host "Of zorg dat er een code op je klembord staat."
    exit
}

# Zorg dat het een string is
$AgbCode = [string]$AgbCode

# Bepaal het pad naar het script
$ScriptPath = Join-Path $PSScriptRoot "agb_checker.py"

# Probeer de Python executable in de virtual environment te vinden
# We checken zowel de Windows-stijl (Scripts) als Unix-stijl (bin)
$VenvPath = Join-Path $PSScriptRoot ".venv"
$PythonWindows = Join-Path $VenvPath "Scripts\python.exe"
$PythonUnix = Join-Path $VenvPath "bin/python"

if (Test-Path $PythonWindows) {
    $PythonExe = $PythonWindows
} elseif (Test-Path $PythonUnix) {
    $PythonExe = $PythonUnix
} else {
    # Fallback naar systeem python als venv niet gevonden is
    $PythonExe = "python"
    # Check of python wel bestaat in path (optioneel, maar netjes)
    try {
        $null = Get-Command $PythonExe -ErrorAction Stop
    } catch {
        Write-Host "FOUT: Geen Python installatie gevonden in .venv of op het systeem." -ForegroundColor Red
        exit 1
    }
}

& $PythonExe $ScriptPath $AgbCode

# AGB Checker Tool

## Wat is het?
Een zelfgeschreven tool om razendsnel AGB-codes te checken in het Vektis register zonder handmatig naar de website te hoeven navigeren en te klikken.

## Hoe werkt het?
Het script (`agb_checker.py`) wordt aangestuurd door een PowerShell wrapper (`check-agb.ps1`) of een Batch script (`agb.bat`).
1. Het haalt een veiligheidstoken op van Vektis.
2. Het zoekt automatisch naar de code als 'Zorgverlener' én 'Onderneming'.
3. Bij een match opent het direct de juiste pagina in je browser.

## Testen
Er is een bestand `test_agb.txt` toegevoegd met een aantal geldige AGB-codes. Je kunt het script testen door deze codes één voor één aan te bieden.

Voorbeeld PowerShell commando om alle testcodes te checken:
```powershell
Get-Content "test_agb.txt" | ForEach-Object { 
    $code = $_.Trim()
    if ($code) { 
        python agb_checker.py $code
        Start-Sleep -Seconds 2
    } 
}
```

## Gebruik op Werk Laptop (Windows)

### 1. Installatie
Zorg dat Python geïnstalleerd is.
Clone de repo of kopieer de map `AGB_checker` naar je `dev` folder.
Installeer dependencies: `pip install -r requirements.txt`

### 2. Alias instellen (Eenmalig)
Je hebt twee opties om het commando `agb` overal te kunnen gebruiken:

**Optie A: PowerShell (Aanbevolen)**
1. Open PowerShell.
2. Typ `code $PROFILE` (of `notepad $PROFILE`).
3. Voeg deze regel toe (pas het pad aan):
   ```powershell
   function agb { C:\Users\JouwNaam\dev\AGB_checker\check-agb.ps1 $args }
   ```
4. Sla op en herstart PowerShell.

**Optie B: Command Prompt / Run (via .bat)**
1. Voeg de map waar `agb.bat` staat toe aan je Windows **PATH** omgevingsvariabele.
2. Nu kun je in elke command prompt of via Win+R simpelweg `agb` typen.

### 3. Dagelijks gebruik
De tool is slim en kijkt naar je klembord als je niets invult.

*   **Scenario A (Meest gebruikt):**
    1. Kopieer een AGB-code (Ctrl+C) uit een mail, Excel of dossier.
    2. Open PowerShell (of Win+R).
    3. Typ `agb` en druk op Enter.
    4. *De browser opent direct met de info.*

*   **Scenario B (Handmatig):**
    1. Typ `agb 01000585`

## Troubleshooting
*   **Geen resultaat?** Check of de code klopt. Het script zoekt exact.
*   **Browser opent niet?** Check of je pop-up blockers hebt of dat het script in 'dry-run' modus draait (standaard niet).
*   **Foutmeldingen?** Waarschijnlijk is Vektis traag of offline. Het script heeft een timeout van 10 seconden.

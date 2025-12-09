# AGB Checker

Een simpele tool om snel AGB-codes te controleren in het Vektis register via de command line.

## Wat doet het?
Het script zoekt automatisch in het Vektis AGB-register naar een opgegeven AGB-code. Het controleert **parallel** of de code toebehoort aan een **Zorgverlener** of een **Onderneming/Vestiging**. Als er een match is, wordt de pagina direct geopend in je standaard browser.

### Performance Optimalisaties
- **Parallel zoeken**: Beide zoektypes worden tegelijkertijd uitgevoerd voor snellere resultaten
- **Geoptimaliseerde HTTP-verbindingen**: Connection pooling en keep-alive voor Windows
- **Snellere HTML parsing**: Gebruikt lxml parser (2-3x sneller dan standaard parser)
- **Vroege exit**: Stopt direct na het vinden van het eerste resultaat

## Installatie

1. Clone deze repository:
   ```bash
   git clone https://github.com/AdMaiora0/AGB_checker.git
   ```
2. Installeer de benodigde Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Gebruik

Je kunt het script aanroepen via het meegeleverde PowerShell script `check-agb.ps1` of via het Batch script `agb.bat`.

**Handmatige invoer:**
```powershell
./check-agb.ps1 01000585
# of
agb.bat 01000585
```

**Via klembord:**
Als je geen code meegeeft, kijkt het script automatisch naar de inhoud van je klembord.
```powershell
./check-agb.ps1
# of
agb.bat
```

## Testen
De repository bevat een bestand `test_agb.txt` met voorbeeldcodes. Je kunt de werking van het script verifiëren door deze codes te gebruiken.

```powershell
# Test alle codes in het bestand (PowerShell)
Get-Content "test_agb.txt" | ForEach-Object { python agb_checker.py $_.Trim() }
```

## Tip voor Windows
### PowerShell
Maak een alias aan in je PowerShell profiel (`code $PROFILE`) om het script overal vandaan aan te kunnen roepen met `agb`:

```powershell
function agb { C:\Pad\Naar\AGB_checker\check-agb.ps1 $args }
```

### Command Prompt (cmd) / Run
Voeg de map waar `agb.bat` staat toe aan je Windows PATH omgevingsvariabele. Dan kun je simpelweg `agb` typen in elke command prompt of in het 'Uitvoeren' (Win+R) venster.
*(Pas het pad aan naar waar je de map hebt opgeslagen)*

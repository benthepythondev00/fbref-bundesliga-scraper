# Multi-Sport Scraper mit Stathead Premium Integration

## 🚀 Schnellstart - Setup nach Betriebssystem

### 🍎 macOS / Linux:
```bash
cd fbref-stathead-scraper
./setup.sh                    # Automatisches Setup
source venv/bin/activate       # Environment aktivieren
python main.py --stathead      # Scraper starten (alle Sportarten)
python main.py --sports bundesliga --bundesliga-mode match  # Bundesliga Match-Modus
```

### 🪟 Windows:
```powershell
cd fbref-stathead-scraper
setup.bat                      # Automatisches Setup (Doppelklick oder in CMD)
venv\Scripts\activate          # Environment aktivieren
python main.py --stathead      # Scraper starten (alle Sportarten)
python main.py --sports bundesliga --bundesliga-mode match  # Bundesliga Match-Modus
```

### ⚡ Noch schneller - Einfach Datei ausführen:
- **macOS/Linux**: Doppelklick auf `setup.sh`
- **Windows**: Doppelklick auf `setup.bat`

## 🆕 PREMIUM-INTEGRATION: Stathead.com

**Stathead Premium-Daten** sind jetzt vollständig integriert! Der Scraper holt automatisch erweiterte Statistiken von Stathead.com zusätzlich zu den Standard-Daten.

### 🔑 Automatische Anmeldung
- **Benutzerdaten**: Bereits in `.env` Datei hinterlegt (R3dn4x/BenScrape5r)
- **Automatischer Login**: Der Scraper meldet sich selbstständig bei Stathead an
- **Keine manuelle Eingabe nötig**: Alles läuft automatisch im Hintergrund

## 📊 Was wird gescraped?

### 🆓 Standard-Daten (kostenlose Quellen)
| Sportart | Teams | Quelle | Daten |
|----------|-------|--------|-------|
| ⚽ Bundesliga | 18 | fbref.com | **Season Mode**: Saison-Tabelle, Team-Stats<br>**Match Mode**: 306 Einzelspiele, Team-Totals pro Match + Kicker.de Tabellenpositionen |
| 🏈 NFL | 32 | pro-football-reference.com | AFC/NFC Standings, Team/Player Stats |
| 🏀 NBA | 30 | basketball-reference.com | East/West Standings, Team/Player Stats |
| 🏒 NHL | 32 | hockey-reference.com | East/West Standings, Skater/Goalie Stats |
| ⚾ MLB | 30 | baseball-reference.com | Batting/Pitching Stats |

### 💎 Premium-Daten (Stathead.com - nur mit `--stathead` Flag)
| Sportart | Teams | Premium-Statistiken |
|----------|-------|-------------------|
| ⚾ Baseball Batting | 30 | Home Runs, RBI, Batting Average, OPS, erweiterte Offensive-Metriken |
| ⚾ Baseball Pitching | 30 | ERA, WHIP, Strikeouts, Advanced Pitching Analytics |
| 🏀 Basketball | 30 | Field Goal %, 3-Point %, True Shooting %, Advanced Team Metrics |
| 🏈 NFL | 32 | Passing Yards, TD Passes, Rushing Stats, Advanced Offensive Analytics |
| 🏒 NHL | 32 | Goals For/Against, Corsi/Fenwick, PDO, Advanced Hockey Metrics |

## 🎯 Verwendungsbeispiele

### Nur Bundesliga scrapen (Standard: Season Mode)
```bash
python main.py --sports bundesliga
```

### Bundesliga Match-by-Match Modus
```bash
python main.py --sports bundesliga --bundesliga-mode match
```

### Bundesliga + NFL
```bash
python main.py --sports bundesliga nfl
```

### US-Sportarten (NFL, NBA, NHL, MLB)
```bash
python main.py --sports nfl nba nhl mlb
```

### Custom Excel-Datei
```bash
python main.py --output meine_statistiken_2025.xlsx
```

### Browser anzeigen (zum Debugging)
```bash
python main.py --headless False
```

### Langsamer scrapen (weniger Requests pro Minute)
```bash
python main.py --rate-limit 5
```

## ⚽ Bundesliga Modi im Detail

### 📊 Season Mode (Standard)
- **Was**: Komplette Saison-Übersicht von der Bundesliga-Hauptseite
- **Daten**: Tabelle + 12 Team-Statistik-Tabellen (Standard Stats, Shooting, Passing, etc.)
- **Schnell**: Nur 1 Seitenaufruf nötig
- **Verwendung**: `python main.py --sports bundesliga` (oder `--bundesliga-mode season`)

### 🎯 Match Mode (Match-by-Match)
- **Was**: Detaillierte Analyse aller 306 Bundesliga-Einzelspiele 2024/25
- **Daten pro Match**:
  - Team-Totals aus 6 FBRef-Statistiktabellen (Summary, Passing, Pass Types, Defensive Actions, Possession, Miscellaneous)
  - Kicker.de Tabellenposition vor dem Spiel (beide Teams)
  - Gegner-Position für Kontext
- **Aufwand**: 306 Seitenaufrufe + Kicker.de Integration
- **Excel**: 18 Team-Sheets (je 34 Spieltage) + Home/Away Aggregation
- **Verwendung**: `python main.py --sports bundesliga --bundesliga-mode match`

## 📁 Output

Nach dem Scraping wird eine Excel-Datei erstellt:
- **Dateiname**: `multi_sport_stats_YYYYMMDD_HHMMSS.xlsx`
- **Ort**: Aktuelles Verzeichnis
- **Inhalt**: Separate Worksheets für jede Liga

### Excel-Struktur

#### Season Mode (Standard)
```
📊 multi_sport_stats_20250923_143022.xlsx
│
├── 📄 Bundesliga 2024-25
│   ├── Tabelle (Rang, Team, Spiele, Tore, Punkte, xG, xGA)
│   └── Team-Statistiken (12 Tabellen)
│
├── 📄 NFL 2024
│   ├── AFC Standings
│   ├── NFC Standings
│   └── Team Stats
│
├── 📄 NBA 2024-25
│   ├── Eastern Conference
│   ├── Western Conference
│   └── Team Stats
│
├── 📄 NHL 2024-25
│   └── Standings & Stats
│
└── 📄 MLB 2024
    ├── Team Batting
    └── Team Pitching
```

#### Match Mode (Match-by-Match)
```
📊 bundesliga_matches_20250923_143022.xlsx
│
├── 📄 Bayern München (34 Zeilen - alle Spiele der Saison)
│   ├── Matchday, Datum, Gegner, Heim/Auswärts
│   ├── Tabellenposition (Bayern + Gegner vor dem Spiel)
│   └── 6 Statistik-Kategorien (je ~15 Parameter)
│
├── 📄 Borussia Dortmund (34 Zeilen)
├── 📄 RB Leipzig (34 Zeilen)
├── 📄 ... (alle 18 Teams)
│
├── 📄 Home Games Summary (alle Heimspiele)
└── 📄 Away Games Summary (alle Auswärtsspiele)
```

## 🔍 Troubleshooting

### Problem: "playwright not found"
**Lösung**:
```bash
source venv/bin/activate
playwright install chromium
```

### Problem: "No module named 'pandas'"
**Lösung**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Timeout-Fehler
**Lösung**: Langsamer scrapen
```bash
python main.py --rate-limit 5
```

### Problem: Keine Daten in Excel
**Mögliche Ursachen**:
1. Website-Struktur hat sich geändert
2. Rate-Limit zu hoch (zu schnell)
3. Netzwerkprobleme

**Debug-Modus**:
```bash
python main.py --headless False
```
(Zeigt Browser-Fenster zum Debugging)

### Logs speichern

```bash
python main.py 2>&1 | tee scraper_log.txt
```

---

**Viel Erfolg mit dem Scraper! 🚀**
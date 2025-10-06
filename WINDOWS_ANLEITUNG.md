# 🪟 Windows Anleitung - Bundesliga Match Scraper

## ⚡ SCHNELLSTART (3 einfache Schritte)

### Schritt 1: Setup ausführen
1. **Doppelklick** auf `setup.bat`
2. Warten bis "Setup completed successfully!" erscheint
3. Fenster schließen (oder Enter drücken)

### Schritt 2: Scraper starten
1. **Doppelklick** auf `RUN_SCRAPER.bat`
2. Der Scraper startet automatisch
3. Warten bis fertig (15-30 Minuten)

### Schritt 3: Excel-Datei öffnen
- Die Datei heißt: `Bundesliga_Matches_2024_25_306_games.xlsx`
- Sie befindet sich im gleichen Ordner

**FERTIG!** ✅

---

## 📋 Was passiert beim Scraping?

Der Scraper holt für **alle 306 Bundesliga-Spiele**:
- ⚽ Team-Statistiken (6 Kategorien pro Team)
- 📊 Torwart-Statistiken
- 📍 Tabellenposition vor dem Spiel (von Kicker.de)
- 🎯 Gegner und dessen Position

**Excel-Struktur:**
- **Gesamt**: Übersicht aller Teams
- **Heim**: Aggregierte Heimspiele
- **Auswärts**: Aggregierte Auswärtsspiele
- **18 Team-Sheets**: Jedes Team hat einen eigenen Reiter mit allen 34 Spieltagen

---

## ❓ Häufige Fragen

### "Muss ich nach setup.bat noch etwas eingeben?"
**Nein!** Einfach `RUN_SCRAPER.bat` doppelklicken - fertig.

### "Was bedeutet 'activate'?"
Das ist ein technischer Befehl, den Sie **nicht manuell** eingeben müssen!
`RUN_SCRAPER.bat` macht das automatisch für Sie.

### "Wo ist die Excel-Datei?"
Im gleichen Ordner wo auch `setup.bat` liegt.

### "Wie lange dauert das Scraping?"
Etwa **15-30 Minuten** für alle 306 Spiele.

### "Kann ich den Computer währenddessen benutzen?"
Ja, aber schließen Sie das Fenster nicht!

---

## 🔧 Problemlösung

### Problem: "Python not found"
**Lösung:**
1. Python installieren von: https://www.python.org/downloads/windows/
2. **Wichtig:** Häkchen bei "Add Python to PATH" setzen!
3. Computer neustarten
4. `setup.bat` nochmal ausführen

### Problem: "Virtual environment not found"
**Lösung:**
`setup.bat` nochmal ausführen.

### Problem: Setup schlägt fehl
**Lösung:**
1. Rechtsklick auf `setup.bat`
2. "Als Administrator ausführen"

### Problem: Scraper bleibt hängen
**Lösung:**
1. Fenster schließen
2. 5 Minuten warten
3. `RUN_SCRAPER.bat` nochmal starten

### Problem: Excel-Datei ist leer
**Lösung:**
Das sollte nicht passieren! Bitte Log-Datei senden:
- `bundesliga_match_scraper.log`

---

## 🚫 NICHT MACHEN

❌ **Nicht** cmd.exe öffnen und Befehle eintippen
❌ **Nicht** "activate" manuell ausführen
❌ **Nicht** Python-Dateien direkt öffnen

✅ **Nur** `RUN_SCRAPER.bat` doppelklicken!

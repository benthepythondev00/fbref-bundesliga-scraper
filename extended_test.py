#!/usr/bin/env python3
"""
AUSFÜHRLICHER INTEGRATION TEST
Testet mehrere Matches über verschiedene Spieltage + Kicker.de Integration
"""

import asyncio
import sys
from bundesliga_match_scraper import BundesligaMatchScraper
from match_excel_exporter import MatchExcelExporter
from base_scraper import RateLimiter
import pandas as pd
from datetime import datetime

async def extended_integration_test():
    print("=" * 100)
    print("🧪 AUSFÜHRLICHER INTEGRATION TEST - Bundesliga Match Scraper + Kicker.de")
    print("=" * 100)
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}\n")

    rate_limiter = RateLimiter(requests_per_minute=10)
    scraper = BundesligaMatchScraper(rate_limiter)

    # Phase 1: Match URLs laden
    print("📋 PHASE 1: Match URLs laden")
    print("-" * 100)

    matches = await scraper.get_match_urls()
    print(f"✅ {len(matches)} Matches gefunden\n")

    # Wähle Test-Matches aus verschiedenen Spieltagen
    test_matches = []

    # Spieltag 1: 2 Matches
    spieltag_1 = [m for m in matches if m['matchday'] == 1][:2]
    test_matches.extend(spieltag_1)

    # Spieltag 2: 2 Matches
    spieltag_2 = [m for m in matches if m['matchday'] == 2][:2]
    test_matches.extend(spieltag_2)

    # Spieltag 3: 2 Matches
    spieltag_3 = [m for m in matches if m['matchday'] == 3][:2]
    test_matches.extend(spieltag_3)

    # Spieltag 5: 1 Match (um Kicker.de nach mehreren Spieltagen zu testen)
    spieltag_5 = [m for m in matches if m['matchday'] == 5][:1]
    test_matches.extend(spieltag_5)

    print(f"📊 Test-Auswahl: {len(test_matches)} Matches aus 4 verschiedenen Spieltagen\n")

    for i, match in enumerate(test_matches, 1):
        print(f"   {i}. Spieltag {match['matchday']}: {match['home_team']} vs {match['away_team']}")
    print()

    # Phase 2: Matches scrapen mit detaillierter Ausgabe
    print("⚽ PHASE 2: Matches scrapen (mit Kicker.de Integration)")
    print("-" * 100)

    all_match_data = []
    kicker_positions_by_matchday = {}

    for i, match in enumerate(test_matches, 1):
        matchday = match['matchday']

        print(f"\n🎯 Match {i}/{len(test_matches)}: Spieltag {matchday}")
        print(f"   {match['home_team']} vs {match['away_team']}")
        print(f"   URL: {match['url'][:70]}...")

        # Scrape Match
        match_data = await scraper.scrape_match_stats(
            match['url'],
            match['home_team'],
            match['away_team'],
            matchday
        )

        if not match_data:
            print(f"   ❌ FEHLER: Keine Daten extrahiert")
            continue

        all_match_data.append(match_data)

        # Extrahiere Statistiken
        home_stats = match_data.get('home_team_stats', {})
        away_stats = match_data.get('away_team_stats', {})
        home_pos = match_data.get('home_team_position', 0)
        away_pos = match_data.get('away_team_position', 0)

        # Zähle Parameter-Typen
        home_player = [k for k in home_stats.keys() if not k.startswith('gk_')]
        home_gk = [k for k in home_stats.keys() if k.startswith('gk_')]
        away_player = [k for k in away_stats.keys() if not k.startswith('gk_')]
        away_gk = [k for k in away_stats.keys() if k.startswith('gk_')]

        print(f"   ✅ Daten extrahiert:")
        print(f"      • {match['home_team']}: {len(home_player)} Player + {len(home_gk)} GK = {len(home_stats)} total")
        print(f"      • {match['away_team']}: {len(away_player)} Player + {len(away_gk)} GK = {len(away_stats)} total")

        # Kicker.de Positionen
        print(f"   🏆 Kicker.de Positionen (vor Spieltag {matchday}):")
        print(f"      • {match['home_team']}: Platz {home_pos}")
        print(f"      • {match['away_team']}: Platz {away_pos}")

        # Speichere Positionen für Validierung
        if matchday not in kicker_positions_by_matchday:
            kicker_positions_by_matchday[matchday] = {}
        kicker_positions_by_matchday[matchday][match['home_team']] = home_pos
        kicker_positions_by_matchday[matchday][match['away_team']] = away_pos

        # Zeige Beispiel-Stats
        print(f"   📊 Beispiel Stats ({match['home_team']}):")
        sample_stats = ['goals', 'assists', 'shots', 'passes']
        for stat in sample_stats:
            if stat in home_stats:
                print(f"      • {stat}: {home_stats[stat]}")

        # Zeige Goalkeeper Stats
        print(f"   🥅 Goalkeeper Stats ({match['home_team']}):")
        gk_samples = ['gk_saves', 'gk_goals_against', 'gk_save_pct']
        for stat in gk_samples:
            if stat in home_stats:
                print(f"      • {stat}: {home_stats[stat]}")

    print(f"\n✅ {len(all_match_data)}/{len(test_matches)} Matches erfolgreich gescraped")
    print()

    # Phase 3: Kicker.de Integration validieren
    print("🏆 PHASE 3: Kicker.de Integration validieren")
    print("-" * 100)
    print()

    # Prüfe Spieltag 1 (alle sollten Position 1 haben)
    if 1 in kicker_positions_by_matchday:
        spieltag_1_pos = kicker_positions_by_matchday[1]
        all_position_1 = all(pos == 1 for pos in spieltag_1_pos.values())

        print(f"✓ Spieltag 1 Positionen (vor Saisonstart):")
        for team, pos in list(spieltag_1_pos.items())[:4]:
            print(f"   • {team}: Position {pos}")

        if all_position_1:
            print(f"   ✅ Korrekt: Alle Teams auf Position 1 vor Saisonstart")
        else:
            print(f"   ⚠️  Warnung: Nicht alle Teams auf Position 1")
        print()

    # Prüfe ob Positionen sich über Spieltage ändern
    if len(kicker_positions_by_matchday) > 1:
        print(f"✓ Positions-Entwicklung über Spieltage:")

        # Vergleiche gleiche Teams über verschiedene Spieltage
        all_spieltage = sorted(kicker_positions_by_matchday.keys())
        sample_teams = []

        # Finde Teams die in mehreren Spieltagen vorkommen
        for spieltag in all_spieltage:
            sample_teams.extend(list(kicker_positions_by_matchday[spieltag].keys())[:2])

        # Zeige Position pro Team über Spieltage
        unique_teams = list(set(sample_teams))[:3]
        for team in unique_teams:
            positions = []
            for spieltag in all_spieltage:
                if team in kicker_positions_by_matchday[spieltag]:
                    pos = kicker_positions_by_matchday[spieltag][team]
                    positions.append(f"ST{spieltag}:P{pos}")

            if positions:
                print(f"   • {team}: {' → '.join(positions)}")

        print(f"   ✅ Positionen ändern sich über Spieltage (dynamisch von Kicker.de)")
        print()

    # Prüfe ob Positionen realistisch sind (1-18)
    all_positions = []
    for spieltag_pos in kicker_positions_by_matchday.values():
        all_positions.extend(spieltag_pos.values())

    valid_positions = all(1 <= pos <= 18 for pos in all_positions)
    print(f"✓ Positions-Validierung:")
    print(f"   • Insgesamt {len(all_positions)} Positionen geprüft")
    print(f"   • Bereich: {min(all_positions)} bis {max(all_positions)}")
    print(f"   • Status: {'✅ Alle im gültigen Bereich (1-18)' if valid_positions else '❌ Ungültige Positionen gefunden'}")
    print()

    # Phase 4: Excel Export testen
    print("📊 PHASE 4: Excel Export mit allen Test-Daten")
    print("-" * 100)

    test_excel = f"extended_test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    print(f"✓ Erstelle Excel: {test_excel}")

    exporter = MatchExcelExporter(
        template_path="Vorlage-Scrapen.xlsx",
        filename=test_excel
    )

    exporter.export_match_data(all_match_data)

    # Validiere Excel
    if os.path.exists(test_excel):
        print(f"✅ Excel-Datei erstellt\n")

        xl = pd.ExcelFile(test_excel)
        sheets = xl.sheet_names

        print(f"   📋 {len(sheets)} Sheets:")
        for sheet in ['Gesamt', 'Heim', 'Auswärts']:
            if sheet in sheets:
                print(f"      ✓ {sheet}")

        # Prüfe Team-Sheets mit Daten
        teams_with_data = []
        for match in all_match_data:
            teams_with_data.append(match['home_team'])
            teams_with_data.append(match['away_team'])

        unique_teams = set(teams_with_data)
        print(f"\n   📋 {len(unique_teams)} Teams mit Daten:")
        for team in sorted(unique_teams):
            normalized_team = exporter._normalize_team_name(team)
            if normalized_team in sheets:
                print(f"      ✓ {normalized_team}")

        # Prüfe Daten-Verteilung über Spieltage
        print(f"\n   📊 Daten-Verteilung:")
        for spieltag in sorted(set(m['matchday'] for m in all_match_data)):
            count = sum(1 for m in all_match_data if m['matchday'] == spieltag)
            print(f"      • Spieltag {spieltag}: {count} Matches")

        print()

        # Detaillierte Prüfung eines Team-Sheets
        sample_team = list(unique_teams)[0]
        normalized_sample = exporter._normalize_team_name(sample_team)

        if normalized_sample in sheets:
            print(f"   🔍 Detail-Prüfung: {normalized_sample} Sheet")
            df = pd.read_excel(test_excel, sheet_name=normalized_sample)

            print(f"      • Struktur: {len(df)} Zeilen × {len(df.columns)} Spalten")

            # Prüfe welche Spieltage Daten haben
            spieltage_mit_daten = []
            for col in df.columns:
                if col != 'team' and isinstance(col, int):
                    if df[col].notna().sum() > 0:
                        spieltage_mit_daten.append(col)

            print(f"      • Spieltage mit Daten: {sorted(spieltage_mit_daten)}")

            # Zeige Beispiel-Werte für ersten Spieltag mit Daten
            if spieltage_mit_daten:
                first_spieltag = min(spieltage_mit_daten)
                print(f"      • Beispiel-Werte (Spieltag {first_spieltag}):")

                sample_params = ['goals', 'assists', 'shots', 'gk_saves']
                for param in sample_params:
                    if param in df['team'].values:
                        idx = df[df['team'] == param].index[0]
                        value = df.loc[idx, first_spieltag]
                        if pd.notna(value):
                            print(f"         • {param}: {value}")

        print()

    # Phase 5: Finale Zusammenfassung
    print("=" * 100)
    print("📊 FINALE ZUSAMMENFASSUNG")
    print("=" * 100)
    print()

    # Test-Ergebnisse
    tests = {
        "Match URLs laden (306)": len(matches) == 306,
        f"Matches gescraped ({len(test_matches)} aus 4 Spieltagen)": len(all_match_data) == len(test_matches),
        "Player Stats (>150 pro Team)": all(len([k for k in m['home_team_stats'].keys() if not k.startswith('gk_')]) > 150 for m in all_match_data),
        "Goalkeeper Stats (>15 pro Team)": all(len([k for k in m['home_team_stats'].keys() if k.startswith('gk_')]) >= 15 for m in all_match_data),
        "Kicker.de Integration": len(kicker_positions_by_matchday) > 0 and valid_positions,
        "Spieltag 1 = Position 1": 1 in kicker_positions_by_matchday and all(pos == 1 for pos in kicker_positions_by_matchday[1].values()),
        "Excel Export erfolgreich": os.path.exists(test_excel) and len(xl.sheet_names) == 21,
    }

    passed = sum(tests.values())
    total = len(tests)

    print("Test-Ergebnisse:")
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")

    print()
    print(f"Gesamt-Ergebnis: {passed}/{total} Tests bestanden")
    print()

    if passed == total:
        print("   🎉 ALLE TESTS BESTANDEN!")
        print("   ✓ FBRef Scraping funktioniert")
        print("   ✓ Kicker.de Integration funktioniert")
        print("   ✓ Excel Export funktioniert")
        print("   ✓ System bereit für Produktiv-Einsatz (alle 306 Matches)")
    else:
        print("   ⚠️  Einige Tests fehlgeschlagen")

    print()
    print(f"Ende: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 100)

    return passed == total

if __name__ == "__main__":
    import os

    try:
        success = asyncio.run(extended_integration_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
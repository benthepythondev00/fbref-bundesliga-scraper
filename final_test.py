#!/usr/bin/env python3
"""
FINALER KOMPLETTER TEST - Bundesliga Match Scraper
Testet ALLE Kundenanforderungen:
1. 306 Matches von Scores & Fixtures
2. 6 Player Stats Tabs (Team Totals)
3. Goalkeeper Stats
4. Beide Teams (Home + Away)
5. Kicker.de Tabellenpositionen
6. Excel Export mit 21 Sheets (Gesamt + 18 Teams + Heim + Auswärts)
"""

import asyncio
import sys
import os
from bundesliga_match_scraper import BundesligaMatchScraper
from match_excel_exporter import MatchExcelExporter
from base_scraper import RateLimiter
import pandas as pd

async def final_test():
    print("=" * 100)
    print("🧪 FINALER KOMPLETTER TEST - BUNDESLIGA MATCH SCRAPER")
    print("=" * 100)
    print()

    # Test 1: Match URLs finden
    print("📋 TEST 1: Match URLs von Scores & Fixtures laden")
    print("-" * 100)

    rate_limiter = RateLimiter(requests_per_minute=10)
    scraper = BundesligaMatchScraper(rate_limiter)

    print("✓ Navigiere zu Bundesliga 2024-25 Scores & Fixtures...")
    matches = await scraper.get_match_urls()

    print(f"✅ {len(matches)} Matches gefunden")
    print(f"   Erwartet: 306 Matches")
    print(f"   Status: {'✅ PASS' if len(matches) == 306 else '❌ FAIL'}")

    if len(matches) != 306:
        print(f"   ⚠️  WARNUNG: {len(matches)} statt 306 Matches!")

    # Zeige erste 3 Matches
    print(f"\n   Erste 3 Matches:")
    for i, match in enumerate(matches[:3], 1):
        print(f"   {i}. Spieltag {match['matchday']}: {match['home_team']} vs {match['away_team']}")
        print(f"      URL: {match['url'][:80]}...")

    print()

    # Test 2: Einen Match scrapen (volle Details)
    print("📊 TEST 2: Match-Details scrapen (alle Tabellen)")
    print("-" * 100)

    test_match = matches[0]  # Erstes Spiel
    print(f"✓ Scrape Match: {test_match['home_team']} vs {test_match['away_team']} (Spieltag {test_match['matchday']})")
    print(f"  URL: {test_match['url']}")
    print()

    match_data = await scraper.scrape_match_stats(
        test_match['url'],
        test_match['home_team'],
        test_match['away_team'],
        test_match['matchday']
    )

    if not match_data:
        print("❌ FAIL: Keine Daten extrahiert!")
        return False

    print("✅ Match-Daten erfolgreich extrahiert\n")

    # Test 3: Player Stats (6 Tabs)
    print("📈 TEST 3: Player Stats (6 Tabs - Team Totals)")
    print("-" * 100)

    home_stats = match_data.get('home_team_stats', {})
    away_stats = match_data.get('away_team_stats', {})

    # Zähle Parameter (ohne gk_ Präfix = Player Stats)
    home_player_params = [k for k in home_stats.keys() if not k.startswith('gk_')]
    away_player_params = [k for k in away_stats.keys() if not k.startswith('gk_')]

    print(f"✓ {test_match['home_team']}: {len(home_player_params)} Player Stats Parameter")
    print(f"✓ {test_match['away_team']}: {len(away_player_params)} Player Stats Parameter")

    # Zeige einige wichtige Parameter
    print(f"\n   Beispiel Player Stats ({test_match['home_team']}):")
    sample_params = ['goals', 'assists', 'shots', 'passes', 'tackles', 'cards_yellow']
    for param in sample_params:
        if param in home_stats:
            print(f"      • {param}: {home_stats[param]}")

    player_stats_ok = len(home_player_params) > 100 and len(away_player_params) > 100
    print(f"\n   Status: {'✅ PASS' if player_stats_ok else '❌ FAIL'}")
    print()

    # Test 4: Goalkeeper Stats
    print("🥅 TEST 4: Goalkeeper Stats")
    print("-" * 100)

    home_gk_params = [k for k in home_stats.keys() if k.startswith('gk_')]
    away_gk_params = [k for k in away_stats.keys() if k.startswith('gk_')]

    print(f"✓ {test_match['home_team']}: {len(home_gk_params)} Goalkeeper Stats Parameter")
    print(f"✓ {test_match['away_team']}: {len(away_gk_params)} Goalkeeper Stats Parameter")

    print(f"\n   Beispiel Goalkeeper Stats ({test_match['home_team']}):")
    gk_sample = ['gk_saves', 'gk_goals_against', 'gk_save_pct', 'gk_shots_on_target_against']
    for param in gk_sample:
        if param in home_stats:
            print(f"      • {param}: {home_stats[param]}")

    gk_stats_ok = len(home_gk_params) >= 15 and len(away_gk_params) >= 15
    print(f"\n   Status: {'✅ PASS' if gk_stats_ok else '❌ FAIL'}")
    print()

    # Test 5: Kicker.de Tabellenpositionen
    print("📊 TEST 5: Kicker.de Tabellenpositionen")
    print("-" * 100)

    home_pos = match_data.get('home_team_position', 0)
    away_pos = match_data.get('away_team_position', 0)

    print(f"✓ {test_match['home_team']}: Position {home_pos}")
    print(f"✓ {test_match['away_team']}: Position {away_pos}")

    positions_ok = 1 <= home_pos <= 18 and 1 <= away_pos <= 18
    print(f"\n   Status: {'✅ PASS' if positions_ok else '❌ FAIL'}")
    print()

    # Test 6: Mehrere Matches scrapen (5 Matches)
    print("🔄 TEST 6: Mehrere Matches scrapen (5 Matches)")
    print("-" * 100)

    all_match_data = []
    test_matches = matches[:5]

    for i, match in enumerate(test_matches, 1):
        print(f"✓ Scrape Match {i}/5: {match['home_team']} vs {match['away_team']} (Spieltag {match['matchday']})...", end='')

        match_result = await scraper.scrape_match_stats(
            match['url'],
            match['home_team'],
            match['away_team'],
            match['matchday']
        )

        if match_result:
            all_match_data.append(match_result)
            print(" ✅")
        else:
            print(" ❌")

    print(f"\n   {len(all_match_data)}/5 Matches erfolgreich gescraped")
    print(f"   Status: {'✅ PASS' if len(all_match_data) == 5 else '❌ FAIL'}")
    print()

    # Test 7: Excel Export
    print("📊 TEST 7: Excel Export (21 Sheets)")
    print("-" * 100)

    test_excel = "test_bundesliga_output.xlsx"
    print(f"✓ Erstelle Excel-Datei: {test_excel}")

    exporter = MatchExcelExporter(
        template_path="Vorlage-Scrapen.xlsx",
        filename=test_excel
    )

    exporter.export_match_data(all_match_data)

    # Prüfe Excel-Datei
    if os.path.exists(test_excel):
        print(f"✅ Excel-Datei erstellt: {test_excel}")

        # Lade Excel und prüfe Sheets
        xl = pd.ExcelFile(test_excel)
        sheets = xl.sheet_names

        print(f"\n   Sheets gefunden: {len(sheets)}")
        print(f"   Erwartet: 21 Sheets (Gesamt + 18 Teams + Heim + Auswärts)")

        # Zeige alle Sheets
        print(f"\n   Sheet-Liste:")
        for sheet in sheets:
            print(f"      • {sheet}")

        # Prüfe wichtige Sheets
        required_sheets = ['Gesamt', 'Heim', 'Auswärts', 'Bayern Munich', 'Dortmund', 'Leverkusen']
        missing_sheets = [s for s in required_sheets if s not in sheets]

        if missing_sheets:
            print(f"\n   ⚠️  Fehlende Sheets: {missing_sheets}")

        excel_ok = len(sheets) == 21 and not missing_sheets
        print(f"\n   Status: {'✅ PASS' if excel_ok else '❌ FAIL'}")
    else:
        print("❌ FAIL: Excel-Datei nicht erstellt!")
        excel_ok = False

    print()

    # Finale Zusammenfassung
    print("=" * 100)
    print("📊 FINALE ZUSAMMENFASSUNG")
    print("=" * 100)

    all_tests = {
        "Match URLs (306 Spiele)": len(matches) == 306,
        "Player Stats (6 Tabs)": player_stats_ok,
        "Goalkeeper Stats": gk_stats_ok,
        "Kicker.de Positionen": positions_ok,
        "Mehrere Matches scrapen": len(all_match_data) == 5,
        "Excel Export (21 Sheets)": excel_ok
    }

    passed = sum(all_tests.values())
    total = len(all_tests)

    print()
    for test_name, result in all_tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")

    print()
    print(f"   Ergebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print()
        print("   🎉 ALLE TESTS BESTANDEN! System ist bereit für Kundenlieferung!")
        print()
    else:
        print()
        print("   ⚠️  Einige Tests fehlgeschlagen. Bitte Fehler prüfen!")
        print()

    print("=" * 100)

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(final_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""
Enhanced Bundesliga Match-by-Match Scraper
Scrapes individual match data from FBRef + Kicker.de table positions
"""

from base_scraper import BaseScraper, ScrapeResult, RateLimiter
from website_analysis import BUNDESLIGA_STRUCTURE
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import pandas as pd
import asyncio

logger = logging.getLogger(__name__)

class BundesligaMatchScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = BUNDESLIGA_STRUCTURE["base_url"]
        self.league_url = BUNDESLIGA_STRUCTURE["league_url"]
        self.config = BUNDESLIGA_STRUCTURE

        # Die 6 FBRef Stat-Tabs die extrahiert werden sollen
        self.stat_tabs = [
            'summary',          # Summary
            'passing',          # Passing
            'passing_types',    # Pass Types
            'defense',          # Defensive Actions
            'possession',       # Possession
            'misc'             # Miscellaneous
        ]

        # Parameter mapping für alle Tabs kombiniert
        self.parameter_mapping = {
            # Summary Stats
            'players_used': 'players_used',
            'avg_age': 'age',
            'possession': 'possession',
            'games': 'games',
            'games_starts': 'games_starts',
            'minutes': 'minutes',
            'minutes_90s': 'minutes_90s',
            'goals': 'goals',
            'assists': 'assists',
            'goals_assists': 'goals_assists',
            'goals_pens': 'goals_pens',
            'pens_made': 'pens_made',
            'pens_att': 'pens_att',
            'cards_yellow': 'cards_yellow',
            'cards_red': 'cards_red',
            'xg': 'xg',
            'npxg': 'npxg',
            'xg_assist': 'xg_assist',
            'npxg_xg_assist': 'npxg_xg_assist',
            'progressive_carries': 'progressive_carries',
            'progressive_passes': 'progressive_passes',

            # Passing Stats
            'passes_completed': 'passes_completed',
            'passes': 'passes',
            'passes_pct': 'passes_pct',
            'passes_total_distance': 'passes_total_distance',
            'passes_progressive_distance': 'passes_progressive_distance',
            'passes_completed_short': 'passes_completed_short',
            'passes_short': 'passes_short',
            'passes_pct_short': 'passes_pct_short',
            'passes_completed_medium': 'passes_completed_medium',
            'passes_medium': 'passes_medium',
            'passes_pct_medium': 'passes_pct_medium',
            'passes_completed_long': 'passes_completed_long',
            'passes_long': 'passes_long',
            'passes_pct_long': 'passes_pct_long',
            'passes_into_final_third': 'passes_into_final_third',
            'passes_into_penalty_area': 'passes_into_penalty_area',
            'crosses_into_penalty_area': 'crosses_into_penalty_area',

            # Pass Types
            'passes_live': 'passes_live',
            'passes_dead': 'passes_dead',
            'passes_free_kicks': 'passes_free_kicks',
            'through_balls': 'through_balls',
            'passes_switches': 'passes_switches',
            'crosses': 'crosses',
            'throw_ins': 'throw_ins',
            'corner_kicks': 'corner_kicks',
            'corner_kicks_in': 'corner_kicks_in',
            'corner_kicks_out': 'corner_kicks_out',
            'corner_kicks_straight': 'corner_kicks_straight',
            'passes_offsides': 'passes_offsides',
            'passes_blocked': 'passes_blocked',

            # Shot Creation/Goal Creation
            'sca': 'sca',
            'sca_per90': 'sca_per90',
            'sca_passes_live': 'sca_passes_live',
            'sca_passes_dead': 'sca_passes_dead',
            'sca_take_ons': 'sca_take_ons',
            'sca_shots': 'sca_shots',
            'sca_fouled': 'sca_fouled',
            'sca_defense': 'sca_defense',
            'gca': 'gca',
            'gca_per90': 'gca_per90',
            'gca_passes_live': 'gca_passes_live',
            'gca_passes_dead': 'gca_passes_dead',
            'gca_take_ons': 'gca_take_ons',
            'gca_shots': 'gca_shots',
            'gca_fouled': 'gca_fouled',
            'gca_defense': 'gca_defense',

            # Defensive Stats
            'tackles': 'tackles',
            'tackles_won': 'tackles_won',
            'tackles_def_3rd': 'tackles_def_3rd',
            'tackles_mid_3rd': 'tackles_mid_3rd',
            'tackles_att_3rd': 'tackles_att_3rd',
            'challenge_tackles': 'challenge_tackles',
            'challenges': 'challenges',
            'challenge_tackles_pct': 'challenge_tackles_pct',
            'challenges_lost': 'challenges_lost',
            'blocks': 'blocks',
            'blocked_shots': 'blocked_shots',
            'blocked_passes': 'blocked_passes',
            'interceptions': 'interceptions',
            'tackles_interceptions': 'tackles_interceptions',
            'clearances': 'clearances',
            'errors': 'errors',

            # Possession Stats
            'touches': 'touches',
            'touches_def_pen_area': 'touches_def_pen_area',
            'touches_def_3rd': 'touches_def_3rd',
            'touches_mid_3rd': 'touches_mid_3rd',
            'touches_att_3rd': 'touches_att_3rd',
            'touches_att_pen_area': 'touches_att_pen_area',
            'touches_live_ball': 'touches_live_ball',
            'take_ons': 'take_ons',
            'take_ons_won': 'take_ons_won',
            'take_ons_won_pct': 'take_ons_won_pct',
            'take_ons_tackled': 'take_ons_tackled',
            'take_ons_tackled_pct': 'take_ons_tackled_pct',
            'carries': 'carries',
            'carries_distance': 'carries_distance',
            'carries_progressive_distance': 'carries_progressive_distance',
            'carries_into_final_third': 'carries_into_final_third',
            'carries_into_penalty_area': 'carries_into_penalty_area',
            'miscontrols': 'miscontrols',
            'dispossessed': 'dispossessed',
            'passes_received': 'passes_received',

            # Miscellaneous Stats
            'fouls': 'fouls',
            'fouled': 'fouled',
            'offsides': 'offsides',
            'pens_won': 'pens_won',
            'pens_conceded': 'pens_conceded',
            'own_goals': 'own_goals',
            'ball_recoveries': 'ball_recoveries',
            'aerials_won': 'aerials_won',
            'aerials_lost': 'aerials_lost',
            'aerials_won_pct': 'aerials_won_pct',

            # Shooting Stats (from summary table)
            'shots': 'shots',
            'shots_on_target': 'shots_on_target',
            'shots_on_target_pct': 'shots_on_target_pct',
            'goals_per_shot': 'goals_per_shot',
            'goals_per_shot_on_target': 'goals_per_shot_on_target',
            'average_shot_distance': 'average_shot_distance',
            'shots_free_kicks': 'shots_free_kicks',

            # Alternative FBRef names (common abbreviations)
            'CrdY': 'cards_yellow',
            'CrdR': 'cards_red',
            'Gls': 'goals',
            'Ast': 'assists',
            'PK': 'pens_made',
            'PKatt': 'pens_att',
            'Sh': 'shots',
            'SoT': 'shots_on_target',
            'SoT%': 'shots_on_target_pct',
            'G/Sh': 'goals_per_shot',
            'G/SoT': 'goals_per_shot_on_target',
            'Dist': 'average_shot_distance',
            'FK': 'shots_free_kicks',
            'PrgP': 'progressive_passes',
            'Cmp': 'passes_completed',
            'Att': 'passes',
            'Cmp%': 'passes_pct',
            'TotDist': 'passes_total_distance',
            'PrgDist': 'passes_progressive_distance',
            'xAG': 'xg_assist',
            'KP': 'passes_into_penalty_area',
            '1/3': 'passes_into_final_third',
            'PPA': 'passes_into_penalty_area',
            'CrsPA': 'crosses_into_penalty_area',
            'Live': 'passes_live',
            'Dead': 'passes_dead',
            'TB': 'through_balls',
            'Sw': 'passes_switches',
            'Crs': 'crosses',
            'TI': 'throw_ins',
            'CK': 'corner_kicks',
            'In': 'corner_kicks_in',
            'Out': 'corner_kicks_out',
            'Str': 'corner_kicks_straight',
            'Off': 'passes_offsides',
            'Blocks': 'passes_blocked',
            'Tkl': 'tackles',
            'TklW': 'tackles_won',
            'Def 3rd': 'tackles_def_3rd',
            'Mid 3rd': 'tackles_mid_3rd',
            'Att 3rd': 'tackles_att_3rd',
            'Tkl': 'challenge_tackles',
            'Att': 'challenges',
            'Tkl%': 'challenge_tackles_pct',
            'Lost': 'challenges_lost',
            'Sh': 'blocked_shots',
            'Pass': 'blocked_passes',
            'Int': 'interceptions',
            'Tkl+Int': 'tackles_interceptions',
            'Clr': 'clearances',
            'Err': 'errors',
            'Touches': 'touches',
            'Def Pen': 'touches_def_pen_area',
            'Def 3rd': 'touches_def_3rd',
            'Mid 3rd': 'touches_mid_3rd',
            'Att 3rd': 'touches_att_3rd',
            'Att Pen': 'touches_att_pen_area',
            'Live': 'touches_live_ball',
            'Att': 'take_ons',
            'Succ': 'take_ons_won',
            'Succ%': 'take_ons_won_pct',
            'Tkld': 'take_ons_tackled',
            'Tkld%': 'take_ons_tackled_pct',
            'Carries': 'carries',
            'TotDist': 'carries_distance',
            'PrgDist': 'carries_progressive_distance',
            '1/3': 'carries_into_final_third',
            'CPA': 'carries_into_penalty_area',
            'Mis': 'miscontrols',
            'Dis': 'dispossessed',
            'Rec': 'passes_received',
            'Fls': 'fouls',
            'Fld': 'fouled',
            'Off': 'offsides',
            'PKwon': 'pens_won',
            'PKcon': 'pens_conceded',
            'OG': 'own_goals',
            'Recov': 'ball_recoveries',
            'Won': 'aerials_won',
            'Lost': 'aerials_lost',
            'Won%': 'aerials_won_pct'
        }

        # Team name mapping for consistency (includes Kicker.de variants with (M, P), (N), etc.)
        self.team_name_mapping = {
            # FBRef names
            'Bor. Mönchengladbach': 'Gladbach',
            'Borussia Dortmund': 'Dortmund',
            'Bayern München': 'Bayern Munich',
            'RB Leipzig': 'Leipzig',
            'Eintracht Frankfurt': 'Frankfurt',
            'TSG Hoffenheim': 'Hoffenheim',
            'SC Freiburg': 'Freiburg',
            'Bayer 04 Leverkusen': 'Leverkusen',
            'VfL Wolfsburg': 'Wolfsburg',
            'Werder Bremen': 'Werder Bremen',
            'FC Augsburg': 'Augsburg',
            '1. FC Union Berlin': 'Union Berlin',
            'VfL Bochum': 'Bochum',
            'VfB Stuttgart': 'Stuttgart',
            '1. FSV Mainz 05': 'Mainz',
            '1. FC Heidenheim': 'Heidenheim',
            'Holstein Kiel': 'Kiel',
            'FC St. Pauli': 'St. Pauli',
            # Kicker.de variants (with Meister/Pokal/Neuling markers)
            'Bayer 04 Leverkusen (M, P)': 'Leverkusen',  # Meister, Pokalsieger
            'Holstein Kiel (N)': 'Kiel',  # Neuling (newcomer)
            'St. Pauli (N)': 'St. Pauli',  # Neuling
            'Heidenheim': 'Heidenheim',  # Sometimes without "1. FC"
            'Mainz': 'Mainz',  # Sometimes without "1. FSV ... 05"
            'Freiburg': 'Freiburg',  # Sometimes without "SC"
            'Wolfsburg': 'Wolfsburg'  # Sometimes without "VfL"
        }

    async def get_kicker_table_positions(self, matchday: int) -> Dict[str, int]:
        """Fetch table positions from Kicker.de for a specific matchday using Playwright"""

        # Before matchday 1, all teams are at position 1
        if matchday <= 1:
            return {team: 1 for team in self.team_name_mapping.values()}

        # For other matchdays, get table after previous matchday
        previous_matchday = matchday - 1
        url = f"https://www.kicker.de/bundesliga/tabelle/2024-25/{previous_matchday}"

        try:
            # Create a new browser context for Kicker.de
            kicker_page = await self.browser.new_page()

            try:
                await kicker_page.goto(url, wait_until='domcontentloaded')

                # Handle cookie dialog if it appears
                try:
                    accept_button = await kicker_page.wait_for_selector('a[href="/"]', timeout=3000)
                    if accept_button:
                        button_text = await accept_button.text_content()
                        if 'Zustimmen' in button_text:
                            await accept_button.click()
                            await kicker_page.wait_for_timeout(1000)
                except:
                    pass  # No cookie dialog or already accepted

                # Extract table positions using Playwright
                positions = await kicker_page.evaluate('''
                    () => {
                        const positions = {};
                        const tableRows = document.querySelectorAll('table.kick__table--ranking tbody tr');

                        tableRows.forEach((row, index) => {
                            const cells = row.querySelectorAll('td');

                            // Skip header row (has <th> elements, not <td>)
                            if (cells.length < 4) return;

                            // Position is in first td cell with class 'kick__table--ranking__rank'
                            const positionCell = row.querySelector('td.kick__table--ranking__rank');
                            const positionText = positionCell ? positionCell.textContent.trim() : '';

                            // Team name is in td.kick__table--ranking__teamname span.kick__table--show-desktop
                            const teamSpan = row.querySelector('td.kick__table--ranking__teamname span.kick__table--show-desktop');
                            const teamName = teamSpan ? teamSpan.textContent.trim() : '';

                            if (teamName && positionText) {
                                const position = parseInt(positionText);
                                if (!isNaN(position)) {
                                    positions[teamName] = position;
                                }
                            }
                        });

                        return positions;
                    }
                ''')

                # Map team names to our format using flexible matching
                mapped_positions = {}
                for kicker_name, position in positions.items():
                    # Remove Kicker.de markers like (M, P), (N), etc. - these change over time!
                    clean_name = kicker_name
                    for marker in [' (M, P)', ' (N)', ' (M)', ' (P)', ' (A)']:
                        clean_name = clean_name.replace(marker, '')
                    clean_name = clean_name.strip()

                    # Try direct mapping first with cleaned name
                    if clean_name in self.team_name_mapping:
                        mapped_positions[self.team_name_mapping[clean_name]] = position
                    elif kicker_name in self.team_name_mapping:
                        mapped_positions[self.team_name_mapping[kicker_name]] = position
                    else:
                        # Fallback: use cleaned name as-is
                        mapped_positions[clean_name] = position

                logger.info(f"Kicker table positions for matchday {previous_matchday}: {mapped_positions}")
                return mapped_positions

            finally:
                await kicker_page.close()

        except Exception as e:
            logger.error(f"Error fetching Kicker table for matchday {matchday}: {e}")
            # Return default positions if failed
            return {team: 1 for team in self.team_name_mapping.values()}

    async def get_match_urls(self) -> List[Dict[str, Any]]:
        """Navigate to Bundesliga fixtures and extract all match URLs"""

        try:
            # Navigate to Bundesliga 2024-25 Scores & Fixtures page (Kunde: 306 Spiele aus 2024-25)
            full_url = f"{self.base_url}/en/comps/20/2024-2025/schedule/2024-2025-Bundesliga-Scores-and-Fixtures"
            await self.navigate_to_url(full_url, wait_for_selector="table.stats_table")

            # Get all match links for the season
            match_links = await self.page.evaluate('''
                () => {
                    const matches = [];
                    const matchRows = document.querySelectorAll('table.stats_table tbody tr');

                    matchRows.forEach(row => {
                        const scoreCell = row.querySelector('td[data-stat="score"]');
                        if (scoreCell) {
                            const scoreLink = scoreCell.querySelector('a');
                            if (scoreLink && scoreLink.href) {
                                const dateCell = row.querySelector('td[data-stat="date"]');
                                const homeTeamCell = row.querySelector('td[data-stat="home_team"]');
                                const awayTeamCell = row.querySelector('td[data-stat="away_team"]');
                                // Fix: Use 'gameweek' instead of 'round' - 'round' contains "Bundesliga", 'gameweek' contains matchday number
                                const gameweekCell = row.querySelector('td[data-stat="gameweek"]');
                                const gameweekText = gameweekCell ? gameweekCell.textContent.trim() : '';

                                // Only process matches with valid gameweek (filters out DFB-Pokal and other competitions)
                                if (dateCell && homeTeamCell && awayTeamCell && gameweekText) {
                                    const matchday = parseInt(gameweekText);
                                    if (!isNaN(matchday)) {
                                        matches.push({
                                            url: scoreLink.href,
                                            date: dateCell.textContent.trim(),
                                            home_team: homeTeamCell.textContent.trim(),
                                            away_team: awayTeamCell.textContent.trim(),
                                            round: gameweekText,
                                            matchday: matchday
                                        });
                                    }
                                }
                            }
                        }
                    });

                    return matches;
                }
            ''')

            logger.info(f"Found {len(match_links)} matches for the season")
            return match_links

        except Exception as e:
            logger.error(f"Error getting match URLs: {e}")
            return []

    async def scrape_match_stats(self, match_url: str, home_team: str, away_team: str, matchday: int) -> Dict[str, Any]:
        """Scrape detailed stats for a single match"""

        try:
            # Don't use wait_for_selector here - cookie consent needs to be handled first
            await self.navigate_to_url(match_url)

            # Wait for stats tables to load (they are loaded dynamically after page load)
            # FBRef loads stats tables via JavaScript after the initial page render
            await asyncio.sleep(8)

            # Wait specifically for keeper stats tables to appear (good indicator that all stats are loaded)
            try:
                await self.page.wait_for_selector('table[id^="keeper_stats_"]', timeout=10000)
            except Exception as e:
                logger.warning(f"Timeout waiting for keeper stats tables: {e}")

            # Extract team IDs from the page
            # Try both player stats tables (stats_*_summary) and keeper tables (keeper_stats_*)
            team_ids = await self.page.evaluate('''
                () => {
                    const teamIds = [];

                    // First try: Player stats summary tables
                    const statsTables = document.querySelectorAll('table[id*="stats_"][id*="_summary"]');
                    statsTables.forEach(table => {
                        const tableId = table.id;
                        const match = tableId.match(/stats_([a-f0-9]+)_summary/);
                        if (match && !teamIds.includes(match[1])) {
                            teamIds.push(match[1]);
                        }
                    });

                    // Second try: Goalkeeper tables (fallback if summary tables not found yet)
                    if (teamIds.length < 2) {
                        const keeperTables = document.querySelectorAll('table[id^="keeper_stats_"]');
                        keeperTables.forEach(table => {
                            const tableId = table.id;
                            const match = tableId.match(/keeper_stats_([a-f0-9]+)/);
                            if (match && !teamIds.includes(match[1])) {
                                teamIds.push(match[1]);
                            }
                        });
                    }

                    return teamIds;
                }
            ''')

            if len(team_ids) < 2:
                logger.error(f"Could not find team IDs for match {match_url}")
                return {}

            # Get table positions before this match
            table_positions = await self.get_kicker_table_positions(matchday)

            # Extract possession from match stats table (customer requirement: "Ballbesitz ist oben aber nicht in den Tabellen")
            possession_data = await self.page.evaluate('''
                () => {
                    // Find the row with "Possession" header in the table
                    const rows = document.querySelectorAll('tr');
                    for (let i = 0; i < rows.length; i++) {
                        const row = rows[i];
                        if (row.textContent.trim() === 'Possession') {
                            // Next row has the percentages
                            const dataRow = rows[i + 1];
                            if (dataRow) {
                                const cells = dataRow.querySelectorAll('td');
                                if (cells.length >= 2) {
                                    const homeStrong = cells[0].querySelector('strong');
                                    const awayStrong = cells[1].querySelector('strong');
                                    return {
                                        home_possession: homeStrong ? parseFloat(homeStrong.textContent.replace('%', '')) : null,
                                        away_possession: awayStrong ? parseFloat(awayStrong.textContent.replace('%', '')) : null
                                    };
                                }
                            }
                        }
                    }
                    return {home_possession: null, away_possession: null};
                }
            ''')

            match_data = {
                'url': match_url,
                'home_team': home_team,
                'away_team': away_team,
                'matchday': matchday,
                'home_team_stats': {'possession': possession_data.get('home_possession')},
                'away_team_stats': {'possession': possession_data.get('away_possession')},
                'home_team_position': table_positions.get(self.team_name_mapping.get(home_team, home_team), 1),
                'away_team_position': table_positions.get(self.team_name_mapping.get(away_team, away_team), 1)
            }

            # Define the stat tables we want to scrape (6 player stats tabs + goalkeeper)
            stat_tables = [
                ('summary', 'Summary'),
                ('passing', 'Passing'),
                ('passing_types', 'Pass Types'),
                ('defense', 'Defensive Actions'),
                ('possession', 'Possession'),
                ('misc', 'Miscellaneous Stats'),
                ('keeper', 'Goalkeeper Stats')  # Added per customer requirement
            ]

            for i, team_id in enumerate(team_ids[:2]):
                team_key = 'home_team_stats' if i == 0 else 'away_team_stats'
                # Initialize with existing data (possession) instead of empty dict
                team_stats = match_data.get(team_key, {})

                for table_type, tab_name in stat_tables:
                    # Goalkeeper stats use different table ID and extraction logic
                    if table_type == 'keeper':
                        table_id = f"keeper_stats_{team_id}"
                    else:
                        table_id = f"stats_{team_id}_{table_type}"

                    # No need to click tabs - all tables are already in the DOM
                    # FBRef loads all 6 player stat tables + goalkeeper table on page load

                    # Extract data: Team totals for player stats, goalkeeper row for keeper stats
                    table_data = await self.page.evaluate(f'''
                        () => {{
                            const table = document.querySelector('#{table_id}');
                            if (!table) return {{}};

                            const rows = table.querySelectorAll('tbody tr[data-row]');
                            if (rows.length === 0) return {{}};

                            let dataRow = null;
                            const isKeeperTable = '{table_type}' === 'keeper';

                            if (isKeeperTable) {{
                                // For goalkeeper stats: Take first row (the goalkeeper)
                                dataRow = rows[0];
                                console.log('Found goalkeeper stats row');
                            }} else {{
                                // For player stats: Find team totals in tfoot
                                // FBRef uses <tfoot> element for team totals (not "16 Players" text)
                                // The team totals row is in <tfoot><tr> with data-stat attributes
                                const tfoot = table.querySelector('tfoot');
                                if (tfoot) {{
                                    // Get the first <tr> in tfoot with data-stat cells
                                    const tfootRow = tfoot.querySelector('tr');
                                    if (tfootRow && tfootRow.querySelectorAll('[data-stat]').length > 0) {{
                                        dataRow = tfootRow;
                                        console.log('Found team totals row in tfoot');
                                    }}
                                }}

                                if (!dataRow) {{
                                    // Fallback: use last row in tbody if no tfoot
                                    dataRow = rows[rows.length - 1];
                                    console.log('Using last tbody row as fallback');
                                }}
                            }}

                            if (!dataRow) return {{}};

                            const cells = dataRow.querySelectorAll('td, th');

                            const rowData = {{}};
                            cells.forEach((cell) => {{
                                // Get data-stat directly from the cell in tfoot (not from thead!)
                                const dataStat = cell.getAttribute('data-stat');
                                const cellText = cell.textContent.trim();

                                if (dataStat && cellText && dataStat !== 'player') {{
                                    rowData[dataStat] = cellText;
                                }}
                            }});

                            return rowData;
                        }}
                    ''')

                    # Store ALL parameters directly from FBRef (no mapping filter!)
                    # This ensures we capture ALL available data from all 6 tabs + goalkeeper
                    for fbref_param, value in table_data.items():
                        if value and value != '':
                            try:
                                # Remove commas and convert to float if possible
                                clean_value = value.replace(',', '')
                                if clean_value.replace('.', '').replace('-', '').isdigit():
                                    team_stats[fbref_param] = float(clean_value)
                                else:
                                    team_stats[fbref_param] = value
                            except:
                                team_stats[fbref_param] = value

                match_data[team_key] = team_stats

            return match_data

        except Exception as e:
            logger.error(f"Error scraping match {match_url}: {e}")
            return {}

    async def scrape_league_standings(self) -> ScrapeResult:
        """For match mode, we scrape all matches instead of just standings"""
        return await self.scrape_all_matches()

    async def scrape_team_stats(self) -> ScrapeResult:
        """For match mode, we scrape all matches instead of just team stats"""
        return await self.scrape_all_matches()

    async def scrape_player_stats(self) -> ScrapeResult:
        """For match mode, we scrape all matches instead of just player stats"""
        return await self.scrape_all_matches()

    async def scrape_all_matches(self) -> ScrapeResult:
        """Scrape all Bundesliga matches for the season"""

        logger.info("Starting Bundesliga match-by-match scraping...")

        try:
            # Get all match URLs
            match_urls = await self.get_match_urls()

            if not match_urls:
                raise Exception("No match URLs found")

            all_match_data = []

            # Process matches in batches to avoid overwhelming the server
            batch_size = 5
            for i in range(0, len(match_urls), batch_size):
                batch = match_urls[i:i + batch_size]

                logger.info(f"Processing batch {i//batch_size + 1}/{(len(match_urls) + batch_size - 1)//batch_size}")

                for match_info in batch:
                    match_data = await self.scrape_match_stats(
                        match_info['url'],
                        match_info['home_team'],
                        match_info['away_team'],
                        match_info['matchday']
                    )

                    if match_data:
                        all_match_data.append(match_data)

                    # Rate limiting
                    await asyncio.sleep(2)

                # Longer pause between batches
                if i + batch_size < len(match_urls):
                    await asyncio.sleep(5)

            return ScrapeResult(
                sport="Bundesliga",
                data_type="match_by_match",
                data=all_match_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error in match-by-match scraping: {e}", exc_info=True)
            return ScrapeResult(
                sport="Bundesliga",
                data_type="match_by_match",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    async def scrape_all(self) -> List[ScrapeResult]:
        """Main scraping method"""
        results = []

        try:
            await self.initialize_browser()

            # Scrape all matches
            match_results = await self.scrape_all_matches()
            results.append(match_results)

            logger.info(f"✅ Bundesliga match scraping completed with {len(results)} result sets")

        except Exception as e:
            logger.error(f"Error in Bundesliga match scrape_all: {e}", exc_info=True)
        finally:
            await self.close_browser()

        return results
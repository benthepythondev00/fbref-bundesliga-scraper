"""
Excel Exporter for Match-by-Match Bundesliga Data
Creates Excel file with team sheets and home/away aggregations
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MatchExcelExporter:
    def __init__(self, template_path: str = None, output_path: str = None, filename: str = None):
        self.template_path = template_path or "Vorlage-Scrapen.xlsx"
        if filename:
            self.output_path = filename
        elif output_path:
            self.output_path = output_path
        else:
            self.output_path = f"bundesliga_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Team names in the correct order for Excel
        self.teams = [
            'Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Frankfurt',
            'Freiburg', 'Gladbach', 'Heidenheim', 'Hoffenheim', 'Kiel',
            'Leverkusen', 'Mainz', 'Leipzig', 'St. Pauli', 'Stuttgart',
            'Union Berlin', 'Werder Bremen', 'Wolfsburg'
        ]

        # Kicker.de team name mapping
        self.kicker_team_mapping = {
            'Bayern München': 'Bayern Munich',
            'Borussia Dortmund': 'Dortmund',
            'RB Leipzig': 'Leipzig',
            'Union Berlin': 'Union Berlin',
            'Eintracht Frankfurt': 'Frankfurt',
            'SC Freiburg': 'Freiburg',
            'Werder Bremen': 'Werder Bremen',
            'VfL Wolfsburg': 'Wolfsburg',
            'FC Augsburg': 'Augsburg',
            'TSG Hoffenheim': 'Hoffenheim',
            '1. FSV Mainz 05': 'Mainz',
            'VfL Bochum': 'Bochum',
            'VfB Stuttgart': 'Stuttgart',
            'Bayer Leverkusen': 'Leverkusen',
            'Borussia Mönchengladbach': 'Gladbach',
            '1. FC Heidenheim': 'Heidenheim',
            'FC St. Pauli': 'St. Pauli',
            'Holstein Kiel': 'Kiel'
        }

        # Cache for Kicker.de table positions
        self._table_positions_cache = {}

    def export_results(self, results):
        """Main export method to match ExcelExporter interface"""
        # Convert results to match_data format if needed
        if hasattr(results[0], 'data') if results else False:
            match_data = [result.data for result in results if result.success]
        else:
            match_data = results

        return self.export_match_data(match_data)

    def export_match_data(self, match_data: List[Dict[str, Any]]):
        """Export match data to Excel with team sheets and home/away aggregations"""

        try:
            # Load the template to get the parameter structure
            template_df = pd.read_excel(self.template_path, sheet_name='Gesamt', index_col=0)
            parameters = template_df.index.tolist()

            # Add Kicker.de position parameters (customer requirement - not in template)
            kicker_params = [
                'table_position_before_match',
                'opponent',
                'opponent_position',
                'venue'
            ]
            for param in kicker_params:
                if param not in parameters:
                    parameters.append(param)

            logger.info(f"Loaded {len(parameters)} parameters from template (including {len(kicker_params)} Kicker.de params)")

            # Create Excel writer
            with pd.ExcelWriter(self.output_path, engine='openpyxl') as writer:

                # Create Gesamt sheet (summary/overview)
                self._create_gesamt_sheet(writer, parameters, match_data)

                # Create individual team sheets
                for team in self.teams:
                    self._create_team_sheet(writer, team, parameters, match_data)

                # Create Home/Away aggregation sheets
                self._create_home_away_sheets(writer, parameters, match_data)

            logger.info(f"Excel file exported successfully: {self.output_path}")
            return self.output_path

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise

    def _create_gesamt_sheet(self, writer, parameters: List[str], match_data: List[Dict[str, Any]]):
        """Create the Gesamt (overview) sheet"""

        # Create empty dataframe with parameters as rows and teams as columns
        df = pd.DataFrame(index=parameters, columns=['team'] + self.teams)
        df['team'] = parameters

        # This sheet typically shows season totals or averages
        # For now, we'll leave it with the parameter structure
        df.to_excel(writer, sheet_name='Gesamt', index=False)

    def _create_team_sheet(self, writer, team_name: str, parameters: List[str], match_data: List[Dict[str, Any]]):
        """Create individual team sheet with 34 matchdays"""

        # Create columns for 34 matchdays
        columns = ['team'] + list(range(1, 35))
        df = pd.DataFrame(index=parameters, columns=columns)
        df['team'] = parameters

        # Fill in match data for this team
        for match in match_data:
            if not match:
                continue

            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            matchday = match.get('matchday', 0)

            # Determine if this team is playing and get their stats
            team_stats = None
            team_position = None
            opponent_position = None
            is_home = False
            opponent = None

            if self._normalize_team_name(home_team) == team_name:
                team_stats = match.get('home_team_stats', {})
                team_position = match.get('home_team_position', 1)  # From scraper
                opponent_position = match.get('away_team_position', 1)  # From scraper
                is_home = True
                opponent = self._normalize_team_name(away_team)
            elif self._normalize_team_name(away_team) == team_name:
                team_stats = match.get('away_team_stats', {})
                team_position = match.get('away_team_position', 1)  # From scraper
                opponent_position = match.get('home_team_position', 1)  # From scraper
                is_home = False
                opponent = self._normalize_team_name(home_team)

            if team_stats and 1 <= matchday <= 34:
                # Intelligent parameter mapping
                mapped_stats = self._map_fbref_to_excel_params(team_stats, parameters)

                # Fill in the mapped stats for this matchday
                for param, value in mapped_stats.items():
                    if param in parameters:
                        df.loc[param, matchday] = value

                # Use table positions from match_data (already fetched by scraper)

                # Add special rows for context data (if they exist in parameters)
                context_data = {
                    'table_position_before_match': team_position,
                    'opponent': opponent,
                    'opponent_position': opponent_position,
                    'venue': 'Home' if is_home else 'Away',
                    'date': match.get('date', ''),
                    'matchday': matchday
                }

                for context_key, context_value in context_data.items():
                    if context_key in parameters:
                        df.loc[context_key, matchday] = context_value

        df.to_excel(writer, sheet_name=team_name, index=False)

    def _create_home_away_sheets(self, writer, parameters: List[str], match_data: List[Dict[str, Any]]):
        """Create Home and Away aggregation sheets"""

        # Prepare data structure for home/away aggregation
        columns = ['team'] + list(range(1, 35))

        # Home sheet - aggregated stats for all home teams per matchday
        home_df = pd.DataFrame(index=parameters, columns=columns)
        home_df['team'] = parameters

        # Away sheet - aggregated stats for all away teams per matchday
        away_df = pd.DataFrame(index=parameters, columns=columns)
        away_df['team'] = parameters

        # Aggregate data by matchday
        for matchday in range(1, 35):
            home_matchday_stats = {}
            away_matchday_stats = {}

            for match in match_data:
                if not match or match.get('matchday') != matchday:
                    continue

                home_stats = match.get('home_team_stats', {})
                away_stats = match.get('away_team_stats', {})

                # Aggregate home team stats
                for param, value in home_stats.items():
                    if param in parameters:
                        if param not in home_matchday_stats:
                            home_matchday_stats[param] = []
                        if isinstance(value, (int, float)):
                            home_matchday_stats[param].append(value)

                # Aggregate away team stats
                for param, value in away_stats.items():
                    if param in parameters:
                        if param not in away_matchday_stats:
                            away_matchday_stats[param] = []
                        if isinstance(value, (int, float)):
                            away_matchday_stats[param].append(value)

            # Calculate aggregated values (sum for most stats)
            for param in parameters:
                if param in home_matchday_stats and home_matchday_stats[param]:
                    home_df.loc[param, matchday] = sum(home_matchday_stats[param])

                if param in away_matchday_stats and away_matchday_stats[param]:
                    away_df.loc[param, matchday] = sum(away_matchday_stats[param])

        home_df.to_excel(writer, sheet_name='Heim', index=False)
        away_df.to_excel(writer, sheet_name='Auswärts', index=False)

    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to match the Excel template format"""

        team_mapping = {
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
            'FC St. Pauli': 'St. Pauli'
        }

        return team_mapping.get(team_name, team_name)

    def get_kicker_table_positions(self, matchday: int) -> Dict[str, int]:
        """Get table positions from Kicker.de before specified matchday"""

        if matchday in self._table_positions_cache:
            return self._table_positions_cache[matchday]

        try:
            if matchday == 1:
                # Before matchday 1, all teams are at position 1
                positions = {team: 1 for team in self.teams}
                self._table_positions_cache[matchday] = positions
                return positions

            # Get table after previous matchday
            previous_matchday = matchday - 1
            url = f"https://www.kicker.de/bundesliga/tabelle/2024-25/{previous_matchday}"

            logger.info(f"Fetching Kicker.de table for matchday {previous_matchday} from {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find table rows
            positions = {}
            rows = soup.select('table tr')

            for i, row in enumerate(rows[1:], 1):  # Skip header row
                if i > 18:  # Only 18 teams
                    break

                # Extract team name from row
                team_cell = row.select_one('td:nth-child(2)')
                if team_cell:
                    team_text = team_cell.get_text(strip=True)

                    # Map Kicker name to our format
                    mapped_team = None
                    for kicker_name, excel_name in self.kicker_team_mapping.items():
                        if kicker_name in team_text:
                            mapped_team = excel_name
                            break

                    if mapped_team:
                        positions[mapped_team] = i
                        logger.debug(f"Position {i}: {team_text} -> {mapped_team}")

            # Fill missing teams with default positions
            for j, team in enumerate(self.teams):
                if team not in positions:
                    positions[team] = j + 1

            self._table_positions_cache[matchday] = positions
            logger.info(f"Successfully cached positions for {len(positions)} teams before matchday {matchday}")
            return positions

        except Exception as e:
            logger.error(f"Error fetching Kicker.de positions for matchday {matchday}: {e}")
            # Fallback: sequential positions
            fallback = {team: i+1 for i, team in enumerate(self.teams)}
            self._table_positions_cache[matchday] = fallback
            return fallback

    def _map_fbref_to_excel_params(self, fbref_stats: Dict[str, Any], excel_params: List[str]) -> Dict[str, Any]:
        """
        Intelligent mapping von FBRef Parametern zu Excel Template Parametern.

        Basiert auf dem Kundenwunsch: automatische Zuordnung auch bei unterschiedlichen Namen.
        """
        mapped_stats = {}

        # Direct mapping rules - based on FBRef parameter names to Excel template
        mapping_rules = {
            # Basic stats
            'goals': 'goals',
            'assists': 'assists',
            'cards_yellow': 'cards_yellow',
            'cards_red': 'cards_red',
            'shots': 'shots',
            'shots_on_target': 'shots_on_target',

            # Passing stats
            'passes_completed': 'passes_completed',
            'passes': 'passes',
            'passes_pct': 'passes_pct',
            'progressive_passes': 'progressive_passes',

            # Advanced stats
            'xg': 'xg',
            'npxg': 'npxg',
            'xg_assist': 'xg_assist',
            'possession': 'possession',

            # Defensive stats
            'tackles': 'tackles',
            'tackles_won': 'tackles_won',
            'interceptions': 'interceptions',
            'blocks': 'blocks',
            'clearances': 'clearances',

            # Alternative naming patterns
            'CrdY': 'cards_yellow',
            'CrdR': 'cards_red',
            'PrgP': 'progressive_passes',
            'xAG': 'xg_assist',
            'GA': 'goals_against',
            'Tklw': 'tackles_won',
            'Int': 'interceptions',
            'Blocks': 'blocks',
            'Clr': 'clearances'
        }

        # First pass: direct mapping
        for fbref_param, excel_param in mapping_rules.items():
            if fbref_param in fbref_stats and excel_param in excel_params:
                mapped_stats[excel_param] = fbref_stats[fbref_param]

        # Second pass: fuzzy matching for unmapped parameters
        for fbref_key, fbref_value in fbref_stats.items():
            if any(mapped_key in mapping_rules for mapped_key in mapped_stats.keys()):
                continue  # Already mapped

            # Try to find similar parameter names in Excel template
            for excel_param in excel_params:
                if self._params_similar(fbref_key, excel_param):
                    mapped_stats[excel_param] = fbref_value
                    logger.debug(f"Fuzzy mapped: {fbref_key} -> {excel_param}")
                    break

        return mapped_stats

    def _params_similar(self, param1: str, param2: str) -> bool:
        """Check if two parameter names are similar enough to map"""
        p1 = param1.lower().replace('_', '').replace('-', '')
        p2 = param2.lower().replace('_', '').replace('-', '')

        # Direct match
        if p1 == p2:
            return True

        # One contains the other
        if p1 in p2 or p2 in p1:
            return True

        # Common abbreviations
        abbrev_mapping = {
            'gls': 'goals',
            'ast': 'assists',
            'sh': 'shots',
            'sot': 'shotstarget',
            'pas': 'passes',
            'tkl': 'tackles',
            'int': 'interceptions'
        }

        p1_normalized = abbrev_mapping.get(p1, p1)
        p2_normalized = abbrev_mapping.get(p2, p2)

        return p1_normalized == p2_normalized
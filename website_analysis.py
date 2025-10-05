"""
COMPREHENSIVE WEBSITE ANALYSIS - Multi-Sport Scraper
Generated: 2025
Analyzed Websites: fbref.com, pro-football-reference.com, basketball-reference.com,
                   hockey-reference.com, baseball-reference.com

Diese Datei enthält alle HTML-Strukturen, CSS-Selektoren und URL-Patterns
für den Multi-Sport Scraper (Bundesliga, NFL, NBA, NHL, MLB)
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TableStructure:
    table_id: str
    caption: str
    css_selector: str
    description: str
    key_columns: List[str]

@dataclass
class URLPattern:
    pattern: str
    example: str
    description: str

BUNDESLIGA_STRUCTURE = {
    "base_url": "https://fbref.com",
    "league_url": "/en/comps/20/2024-2025/2024-2025-Bundesliga-Stats",

    "tables": {
        "standings": TableStructure(
            table_id="results2024-2025201_overall",
            caption="Bundesliga Table",
            css_selector="table#results2024-2025201_overall",
            description="Liga-Tabelle mit Standings",
            key_columns=["Rk", "Squad", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts", "xG", "xGA"]
        ),
        "standard_stats": TableStructure(
            table_id="stats_squads_standard_for",
            caption="Squad Standard Stats",
            css_selector="table#stats_squads_standard_for",
            description="Team Standard Statistics",
            key_columns=["Squad", "# Pl", "Age", "Poss", "MP", "Starts", "Min", "90s", "Gls", "Ast", "xG", "npxG", "xAG"]
        ),
        "shooting_stats": TableStructure(
            table_id="stats_squads_shooting_for",
            caption="Squad Shooting Stats",
            css_selector="table#stats_squads_shooting_for",
            description="Team Shooting Statistics",
            key_columns=["Squad", "90s", "Gls", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90"]
        ),
        "passing_stats": TableStructure(
            table_id="stats_squads_passing_for",
            caption="Squad Passing Stats",
            css_selector="table#stats_squads_passing_for",
            description="Team Passing Statistics",
            key_columns=["Squad", "90s", "Cmp", "Att", "Cmp%", "TotDist", "PrgDist"]
        ),
        "passing_types": TableStructure(
            table_id="stats_squads_passing_types_for",
            caption="Squad Passing Types",
            css_selector="table#stats_squads_passing_types_for",
            description="Team Passing Types Statistics",
            key_columns=["Squad", "90s", "Att", "Live", "Dead", "FK", "TB", "Sw", "Crs"]
        ),
        "goal_shot_creation": TableStructure(
            table_id="stats_squads_gca_for",
            caption="Squad Goal and Shot Creation",
            css_selector="table#stats_squads_gca_for",
            description="Team Goal and Shot Creation Statistics",
            key_columns=["Squad", "90s", "SCA", "SCA90", "PassLive", "PassDead", "TO", "Sh", "Fld", "Def"]
        ),
        "defense_stats": TableStructure(
            table_id="stats_squads_defense_for",
            caption="Squad Defensive Actions",
            css_selector="table#stats_squads_defense_for",
            description="Team Defensive Statistics",
            key_columns=["Squad", "90s", "Tkl", "TklW", "Def 3rd", "Mid 3rd", "Att 3rd", "Blocks"]
        ),
        "possession_stats": TableStructure(
            table_id="stats_squads_possession_for",
            caption="Squad Possession",
            css_selector="table#stats_squads_possession_for",
            description="Team Possession Statistics",
            key_columns=["Squad", "90s", "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Att 3rd", "Att Pen"]
        ),
        "playing_time": TableStructure(
            table_id="stats_squads_playing_time_for",
            caption="Squad Playing Time",
            css_selector="table#stats_squads_playing_time_for",
            description="Team Playing Time Statistics",
            key_columns=["Squad", "MP", "Min", "Mn/MP", "Min%", "90s", "Starts"]
        ),
        "misc_stats": TableStructure(
            table_id="stats_squads_misc_for",
            caption="Squad Miscellaneous Stats",
            css_selector="table#stats_squads_misc_for",
            description="Team Miscellaneous Statistics",
            key_columns=["Squad", "90s", "CrdY", "CrdR", "2CrdY", "Fls", "Fld", "Off", "Crs", "Int"]
        ),
        "goalkeeping": TableStructure(
            table_id="stats_squads_keeper_for",
            caption="Squad Goalkeeping",
            css_selector="table#stats_squads_keeper_for",
            description="Team Goalkeeping Statistics",
            key_columns=["Squad", "90s", "GA", "GA90", "SoTA", "Saves", "Save%", "W", "D", "L"]
        ),
        "advanced_goalkeeping": TableStructure(
            table_id="stats_squads_keeper_adv_for",
            caption="Squad Advanced Goalkeeping",
            css_selector="table#stats_squads_keeper_adv_for",
            description="Team Advanced Goalkeeping Statistics",
            key_columns=["Squad", "90s", "GA", "PKA", "FK", "CK", "OG", "PSxG", "PSxG/SoT"]
        )
    },

    "url_patterns": {
        "team": URLPattern(
            pattern="/en/squads/{team_id}/2024-2025/{team_name}-Stats",
            example="/en/squads/054efa67/2024-2025/Bayern-Munich-Stats",
            description="Team-Seiten URL-Pattern"
        ),
        "player": URLPattern(
            pattern="/en/players/{player_id}/{player_name}",
            example="/en/players/21a66f6a/Harry-Kane",
            description="Player-Profil URL-Pattern"
        )
    },

    "css_selectors": {
        "team_links": "table#results2024-2025201_overall a[href*='/squads/']",
        "player_links": "table#stats_standard_20 a[href*='/players/']",
        "stats_tables": "table.stats_table",
        "table_rows": "tbody tr",
        "table_headers": "thead th"
    }
}

NFL_STRUCTURE = {
    "base_url": "https://www.pro-football-reference.com",
    "league_url": "/years/2024/",

    "tables": {
        "afc_standings": TableStructure(
            table_id="AFC",
            caption="AFC Standings",
            css_selector="table#AFC",
            description="AFC Conference Standings",
            key_columns=["Team", "W", "L", "W-L%", "PF", "PA", "PD", "MoV", "SoS", "SRS", "OSRS", "DSRS"]
        ),
        "nfc_standings": TableStructure(
            table_id="NFC",
            caption="NFC Standings",
            css_selector="table#NFC",
            description="NFC Conference Standings",
            key_columns=["Team", "W", "L", "W-L%", "PF", "PA", "PD", "MoV", "SoS", "SRS", "OSRS", "DSRS"]
        ),
        "team_stats": TableStructure(
            table_id="team_stats",
            caption="Team Stats and Rankings",
            css_selector="table#team_stats",
            description="Team-Statistiken Overview",
            key_columns=["Team", "W", "L", "T", "PF", "PA", "PD", "Ply", "Ply_Off", "Ply_Def"]
        ),
        "passing_stats": TableStructure(
            table_id="passing",
            caption="Passing Table",
            css_selector="table#passing",
            description="Player Passing Statistics",
            key_columns=["Rk", "Player", "Age", "Pos", "G", "GS", "QBrec", "Cmp", "Att", "Cmp%", "Yds", "TD", "Int", "Rate", "QBR"]
        )
    },

    "url_patterns": {
        "team": URLPattern(
            pattern="/teams/{team_code}/2024.htm",
            example="/teams/kan/2024.htm",
            description="NFL Team-Seiten (Kansas City Chiefs)"
        ),
        "player": URLPattern(
            pattern="/players/{first_letter}/{player_id}.htm",
            example="/players/M/MahoPa00.htm",
            description="NFL Player-Profil (Patrick Mahomes)"
        )
    },

    "css_selectors": {
        "team_links": "table#AFC a[href*='/teams/'], table#NFC a[href*='/teams/']",
        "player_links": "table#passing a[href*='/players/']",
        "stats_tables": "table.stats_table",
        "table_rows": "tbody tr",
        "table_headers": "thead th"
    }
}

NBA_STRUCTURE = {
    "base_url": "https://www.basketball-reference.com",
    "league_url": "/leagues/NBA_2025.html",

    "tables": {
        "east_standings": TableStructure(
            table_id="confs_standings_E",
            caption="Eastern Conference Standings",
            css_selector="table#confs_standings_E",
            description="Eastern Conference Standings",
            key_columns=["Team", "W", "L", "W/L%", "GB", "PS/G", "PA/G", "SRS"]
        ),
        "west_standings": TableStructure(
            table_id="confs_standings_W",
            caption="Western Conference Standings",
            css_selector="table#confs_standings_W",
            description="Western Conference Standings",
            key_columns=["Team", "W", "L", "W/L%", "GB", "PS/G", "PA/G", "SRS"]
        ),
        "team_stats": TableStructure(
            table_id="per_game-team",
            caption="Per Game Stats Table",
            css_selector="table#per_game-team",
            description="Team Per Game Statistics",
            key_columns=["Rk", "Team", "G", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
        )
    },

    "url_patterns": {
        "team": URLPattern(
            pattern="/teams/{team_code}/2025.html",
            example="/teams/BOS/2025.html",
            description="NBA Team-Seiten (Boston Celtics)"
        ),
        "player": URLPattern(
            pattern="/players/{first_letter}/{player_id}.html",
            example="/players/t/tatumja01.html",
            description="NBA Player-Profil"
        )
    },

    "css_selectors": {
        "team_links": "table#confs_standings_E a[href*='/teams/'], table#confs_standings_W a[href*='/teams/']",
        "player_links": "table a[href*='/players/']",
        "stats_tables": "table.stats_table",
        "table_rows": "tbody tr",
        "table_headers": "thead th"
    }
}

NHL_STRUCTURE = {
    "base_url": "https://www.hockey-reference.com",
    "league_url": "/leagues/NHL_2025.html",

    "tables": {
        "east_standings": TableStructure(
            table_id="standings_EAS",
            caption="Eastern Conference Standings",
            css_selector="table#standings_EAS",
            description="Eastern Conference Standings",
            key_columns=["Team", "GP", "W", "L", "OL", "PTS", "PTS%", "GF", "GA", "SRS", "SOS"]
        ),
        "west_standings": TableStructure(
            table_id="standings_WES",
            caption="Western Conference Standings",
            css_selector="table#standings_WES",
            description="Western Conference Standings",
            key_columns=["Team", "GP", "W", "L", "OL", "PTS", "PTS%", "GF", "GA", "SRS", "SOS"]
        ),
        "team_stats": TableStructure(
            table_id="stats",
            caption="Team Stats",
            css_selector="table#stats",
            description="Team Statistics",
            key_columns=["Team", "AvAge", "GP", "W", "L", "OL", "PTS", "PTS%", "GF", "GA", "SOW", "SOL", "SRS", "SOS"]
        )
    },

    "url_patterns": {
        "team": URLPattern(
            pattern="/teams/{team_code}/2025.html",
            example="/teams/FLA/2025.html",
            description="NHL Team-Seiten (Florida Panthers)"
        ),
        "player": URLPattern(
            pattern="/players/{first_letter}/{player_id}.html",
            example="/players/m/mcdavco01.html",
            description="NHL Player-Profil"
        )
    },

    "css_selectors": {
        "team_links": "table#standings_EAS a[href*='/teams/'], table#standings_WES a[href*='/teams/']",
        "player_links": "table a[href*='/players/']",
        "stats_tables": "table.stats_table",
        "table_rows": "tbody tr",
        "table_headers": "thead th"
    }
}

MLB_STRUCTURE = {
    "base_url": "https://www.baseball-reference.com",
    "league_url": "/leagues/majors/2024.shtml",

    "tables": {
        "batting_stats": TableStructure(
            table_id="teams_standard_batting",
            caption="Team Standard Batting",
            css_selector="table#teams_standard_batting",
            description="Team Batting Statistics",
            key_columns=["Tm", "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB", "CS", "BB", "SO", "BA", "OBP", "SLG", "OPS"]
        ),
        "pitching_stats": TableStructure(
            table_id="teams_standard_pitching",
            caption="Team Standard Pitching",
            css_selector="table#teams_standard_pitching",
            description="Team Pitching Statistics",
            key_columns=["Tm", "W", "L", "W-L%", "ERA", "G", "GS", "GF", "CG", "SHO", "SV", "IP", "H", "R", "ER", "HR", "BB", "SO", "WHIP"]
        )
    },

    "url_patterns": {
        "team": URLPattern(
            pattern="/teams/{team_code}/2024.shtml",
            example="/teams/LAD/2024.shtml",
            description="MLB Team-Seiten (Los Angeles Dodgers)"
        ),
        "player": URLPattern(
            pattern="/players/{first_letter}/{player_id}.shtml",
            example="/players/o/ohtansh01.shtml",
            description="MLB Player-Profil"
        )
    },

    "css_selectors": {
        "team_links": "table#teams_standard_batting a[href*='/teams/']",
        "player_links": "table a[href*='/players/']",
        "stats_tables": "table.stats_table",
        "table_rows": "tbody tr",
        "table_headers": "thead th"
    }
}

SCRAPING_CONFIG = {
    "rate_limiting": {
        "requests_per_minute": 10,
        "delay_between_requests": 6,
        "max_retries": 3,
        "retry_delay": 30
    },

    "playwright_config": {
        "headless": True,
        "timeout": 60000,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    },

    "anti_detection": {
        "randomize_delays": True,
        "min_delay": 3,
        "max_delay": 8,
        "rotate_user_agents": True,
        "simulate_human_behavior": True
    }
}

EXCEL_CONFIG = {
    "bundesliga": {
        "worksheet_name": "Bundesliga 2024-25",
        "team_count": 18,
        "key_stats": ["Rk", "Squad", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts", "xG", "xGA"]
    },
    "nfl": {
        "worksheet_name": "NFL 2024",
        "team_count": 32,
        "key_stats": ["Team", "W", "L", "W-L%", "PF", "PA", "PD", "MoV"]
    },
    "nba": {
        "worksheet_name": "NBA 2024-25",
        "team_count": 30,
        "key_stats": ["Team", "W", "L", "W/L%", "PTS", "FG%", "3P%", "FT%"]
    },
    "nhl": {
        "worksheet_name": "NHL 2024-25",
        "team_count": 32,
        "key_stats": ["Team", "GP", "W", "L", "OL", "PTS", "GF", "GA"]
    },
    "mlb": {
        "worksheet_name": "MLB 2024",
        "team_count": 30,
        "key_stats": ["Tm", "W", "L", "W-L%", "R", "H", "HR", "BA", "ERA"]
    }
}

ALL_SPORTS = {
    "bundesliga": BUNDESLIGA_STRUCTURE,
    "nfl": NFL_STRUCTURE,
    "nba": NBA_STRUCTURE,
    "nhl": NHL_STRUCTURE,
    "mlb": MLB_STRUCTURE
}
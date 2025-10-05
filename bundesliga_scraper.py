"""
Bundesliga Scraper - FBref.com
Scrapes Bundesliga 2024-2025 Season Data
"""

from base_scraper import BaseScraper, ScrapeResult, RateLimiter
from website_analysis import BUNDESLIGA_STRUCTURE
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BundesligaScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = BUNDESLIGA_STRUCTURE["base_url"]
        self.league_url = BUNDESLIGA_STRUCTURE["league_url"]
        self.config = BUNDESLIGA_STRUCTURE

    async def scrape_league_standings(self) -> ScrapeResult:
        logger.info("Scraping Bundesliga standings...")

        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#results2024-2025201_overall")

            standings_data = await self.extract_table_data("table#results2024-2025201_overall")

            team_links = await self.extract_links(
                self.config["css_selectors"]["team_links"],
                self.base_url
            )

            result_data = [{
                "standings": standings_data,
                "team_urls": team_links,
                "total_teams": len(team_links)
            }]

            return ScrapeResult(
                sport="Bundesliga",
                data_type="standings",
                data=result_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error scraping Bundesliga standings: {e}", exc_info=True)
            return ScrapeResult(
                sport="Bundesliga",
                data_type="standings",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    async def scrape_all_team_stats_from_main_page(self) -> ScrapeResult:
        """Scrapt alle 12 Team-Statistik-Tabellen direkt von der Bundesliga-Hauptseite"""
        logger.info("Scraping all team stats from main page...")

        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#results2024-2025201_overall")

            # Alle 12 Tabellen-IDs die auf der Hauptseite verfügbar sind
            table_configs = {
                "standings": "results2024-2025201_overall",
                "standard_stats": "stats_squads_standard_for",
                "shooting_stats": "stats_squads_shooting_for",
                "passing_stats": "stats_squads_passing_for",
                "passing_types": "stats_squads_passing_types_for",
                "goal_shot_creation": "stats_squads_gca_for",
                "defense_stats": "stats_squads_defense_for",
                "possession_stats": "stats_squads_possession_for",
                "playing_time": "stats_squads_playing_time_for",
                "misc_stats": "stats_squads_misc_for",
                "goalkeeping": "stats_squads_keeper_for",
                "advanced_goalkeeping": "stats_squads_keeper_adv_for"
            }

            all_tables = {}
            season = "2024-2025"

            for table_name, table_id in table_configs.items():
                try:
                    logger.info(f"Extracting table: {table_name} (#{table_id})")
                    table_data = await self.extract_table_data(f"table#{table_id}")

                    if table_data:
                        # Füge Season Information zu jeder Zeile hinzu
                        for row in table_data:
                            row['season'] = season
                            row['table_source'] = table_name

                        all_tables[table_name] = table_data
                        logger.info(f"Successfully extracted {len(table_data)} rows from {table_name}")
                    else:
                        logger.warning(f"No data found for table {table_name} (#{table_id})")

                except Exception as e:
                    logger.warning(f"Could not extract {table_name} (#{table_id}): {e}")

            result_data = [{
                "season": season,
                "league": "Bundesliga",
                "tables": all_tables,
                "table_count": len(all_tables),
                "source_url": full_url
            }]

            return ScrapeResult(
                sport="Bundesliga",
                data_type="all_team_stats",
                data=result_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error scraping all team stats from main page: {e}", exc_info=True)
            return ScrapeResult(
                sport="Bundesliga",
                data_type="all_team_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    async def scrape_all(self) -> List[ScrapeResult]:
        """Überschreibt die Standard-Methode um alle Team-Stats von der Hauptseite zu scrapen"""
        results = []

        try:
            await self.initialize_browser()

            # Scrape die Bundesliga-Tabelle für Links
            standings = await self.scrape_league_standings()
            results.append(standings)

            # Scrape alle Team-Statistiken direkt von der Hauptseite (anstatt einzelne Team-Seiten zu besuchen)
            all_team_stats = await self.scrape_all_team_stats_from_main_page()
            results.append(all_team_stats)

            logger.info(f"✅ Bundesliga scraping completed with {len(results)} result sets")

        except Exception as e:
            logger.error(f"Error in Bundesliga scrape_all: {e}", exc_info=True)
        finally:
            await self.close_browser()

        return results

    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        """Dummy-Implementierung - wird nicht mehr verwendet"""
        logger.warning("scrape_team_stats is deprecated - use scrape_all_team_stats_from_main_page instead")
        return ScrapeResult(
            sport="Bundesliga",
            data_type="deprecated_team_stats",
            data=[],
            timestamp=datetime.now(),
            success=False,
            error_message="This method is deprecated"
        )

    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        """Dummy-Implementierung - wird nicht mehr verwendet"""
        logger.warning("scrape_player_stats is deprecated - player stats are no longer scraped")
        return ScrapeResult(
            sport="Bundesliga",
            data_type="deprecated_player_stats",
            data=[],
            timestamp=datetime.now(),
            success=False,
            error_message="Player stats are no longer scraped"
        )
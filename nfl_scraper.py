"""
NFL Scraper - Pro-Football-Reference.com
Scrapes NFL 2024 Season Data
"""

from base_scraper import BaseScraper, ScrapeResult, RateLimiter
from website_analysis import NFL_STRUCTURE
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NFLScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = NFL_STRUCTURE["base_url"]
        self.league_url = NFL_STRUCTURE["league_url"]
        self.config = NFL_STRUCTURE

    async def scrape_league_standings(self) -> ScrapeResult:
        logger.info("Scraping NFL standings...")

        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#AFC")

            afc_standings = await self.extract_table_data("table#AFC")
            nfc_standings = await self.extract_table_data("table#NFC")

            team_links = await self.extract_links(
                self.config["css_selectors"]["team_links"],
                self.base_url
            )

            result_data = [{
                "afc_standings": afc_standings,
                "nfc_standings": nfc_standings,
                "team_urls": team_links,
                "total_teams": len(team_links)
            }]

            return ScrapeResult(
                sport="NFL",
                data_type="standings",
                data=result_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error scraping NFL standings: {e}", exc_info=True)
            return ScrapeResult(
                sport="NFL",
                data_type="standings",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        logger.info(f"Scraping NFL team stats from: {team_url}")

        try:
            await self.navigate_to_url(team_url, wait_for_selector="table#team_stats")

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            team_stats = await self.extract_table_data("table#team_stats")
            passing_stats = await self.extract_table_data("table#passing")
            rushing_stats = await self.extract_table_data("table#rushing_and_receiving")
            defense_stats = await self.extract_table_data("table#defense")

            for row in team_stats:
                row['team'] = team_name
                row['season'] = '2024'
            for row in passing_stats:
                row['team'] = team_name
                row['season'] = '2024'
            for row in rushing_stats:
                row['team'] = team_name
                row['season'] = '2024'
            for row in defense_stats:
                row['team'] = team_name
                row['season'] = '2024'

            result_data = [{
                "team_url": team_url,
                "team_stats": team_stats,
                "passing_stats": passing_stats,
                "rushing_stats": rushing_stats,
                "defense_stats": defense_stats
            }]

            return ScrapeResult(
                sport="NFL",
                data_type="team_stats",
                data=result_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error scraping NFL team stats: {e}", exc_info=True)
            return ScrapeResult(
                sport="NFL",
                data_type="team_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        logger.info(f"Scraping NFL player stats from: {team_url}")

        try:
            await self.navigate_to_url(team_url, wait_for_selector="table#passing")

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            passing_players = await self.extract_table_data("table#passing")
            rushing_players = await self.extract_table_data("table#rushing_and_receiving")

            for player in passing_players:
                player['team'] = team_name
                player['season'] = '2024'
            for player in rushing_players:
                player['team'] = team_name
                player['season'] = '2024'

            result_data = [{
                "team_url": team_url,
                "passing_players": passing_players,
                "rushing_players": rushing_players
            }]

            return ScrapeResult(
                sport="NFL",
                data_type="player_stats",
                data=result_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error scraping NFL player stats: {e}", exc_info=True)
            return ScrapeResult(
                sport="NFL",
                data_type="player_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
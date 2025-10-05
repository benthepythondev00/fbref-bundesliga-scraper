"""
NBA, NHL, MLB Scrapers - Sports-Reference.com
Scrapes 2024-2025 Season Data for Basketball, Hockey, Baseball
"""

from base_scraper import BaseScraper, ScrapeResult, RateLimiter
from website_analysis import NBA_STRUCTURE, NHL_STRUCTURE, MLB_STRUCTURE
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class NBAScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = NBA_STRUCTURE["base_url"]
        self.league_url = NBA_STRUCTURE["league_url"]
        self.config = NBA_STRUCTURE

    async def scrape_league_standings(self) -> ScrapeResult:
        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#confs_standings_E")

            east_standings = await self.extract_table_data("table#confs_standings_E")
            west_standings = await self.extract_table_data("table#confs_standings_W")
            team_links = await self.extract_links(self.config["css_selectors"]["team_links"], self.base_url)

            return ScrapeResult(
                sport="NBA", data_type="standings",
                data=[{"east": east_standings, "west": west_standings, "team_urls": team_links}],
                timestamp=datetime.now(), success=True
            )
        except Exception as e:
            logger.error(f"NBA standings error: {e}")
            return ScrapeResult(sport="NBA", data_type="standings", data=[], timestamp=datetime.now(), success=False, error_message=str(e))

    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table")

            # Wait a bit for page to fully load
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            # Extract tables with better error handling
            roster = await self.extract_table_data("table#roster")
            stats = await self.extract_table_data("table#per_game")

            # Add team and season info
            for row in roster:
                row['team'] = team_name
                row['season'] = '2024-25'
            for row in stats:
                row['team'] = team_name
                row['season'] = '2024-25'

            logger.info(f"✅ NBA team stats successful for {team_name}: {len(roster)} roster, {len(stats)} stats")
            return ScrapeResult(
                sport="NBA",
                data_type="team_stats",
                data=[{"roster": roster, "stats": stats}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"NBA team stats timeout for {team_url}: {e}")
            else:
                logger.error(f"NBA team stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="NBA",
                data_type="team_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )

    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table#per_game")

            # Wait a bit for page to fully load
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            player_stats = await self.extract_table_data("table#per_game")

            # Add team and season info
            for player in player_stats:
                player['team'] = team_name
                player['season'] = '2024-25'

            logger.info(f"✅ NBA player stats successful for {team_name}: {len(player_stats)} players")
            return ScrapeResult(
                sport="NBA",
                data_type="player_stats",
                data=[{"players": player_stats}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"NBA player stats timeout for {team_url}: {e}")
            else:
                logger.error(f"NBA player stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="NBA",
                data_type="player_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )

class NHLScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = NHL_STRUCTURE["base_url"]
        self.league_url = NHL_STRUCTURE["league_url"]
        self.config = NHL_STRUCTURE

    async def scrape_league_standings(self) -> ScrapeResult:
        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#standings_EAS")

            east_standings = await self.extract_table_data("table#standings_EAS")
            west_standings = await self.extract_table_data("table#standings_WES")
            team_links = await self.extract_links(self.config["css_selectors"]["team_links"], self.base_url)

            return ScrapeResult(
                sport="NHL", data_type="standings",
                data=[{"east": east_standings, "west": west_standings, "team_urls": team_links}],
                timestamp=datetime.now(), success=True
            )
        except Exception as e:
            logger.error(f"NHL standings error: {e}")
            return ScrapeResult(sport="NHL", data_type="standings", data=[], timestamp=datetime.now(), success=False, error_message=str(e))

    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table")
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            roster = await self.extract_table_data("table#roster")
            skaters = await self.extract_table_data("table#skaters")
            goalies = await self.extract_table_data("table#goalies")

            for row in roster:
                row['team'] = team_name
                row['season'] = '2024-25'
            for row in skaters:
                row['team'] = team_name
                row['season'] = '2024-25'
            for row in goalies:
                row['team'] = team_name
                row['season'] = '2024-25'

            logger.info(f"✅ NHL team stats successful for {team_name}: {len(roster)} roster, {len(skaters)} skaters, {len(goalies)} goalies")
            return ScrapeResult(
                sport="NHL",
                data_type="team_stats",
                data=[{"roster": roster, "skaters": skaters, "goalies": goalies}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"NHL team stats timeout for {team_url}: {e}")
            else:
                logger.error(f"NHL team stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="NHL",
                data_type="team_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )

    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table#skaters")
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            player_stats = await self.extract_table_data("table#skaters")

            for player in player_stats:
                player['team'] = team_name
                player['season'] = '2024-25'

            logger.info(f"✅ NHL player stats successful for {team_name}: {len(player_stats)} players")
            return ScrapeResult(
                sport="NHL",
                data_type="player_stats",
                data=[{"players": player_stats}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"NHL player stats timeout for {team_url}: {e}")
            else:
                logger.error(f"NHL player stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="NHL",
                data_type="player_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )

class MLBScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = MLB_STRUCTURE["base_url"]
        self.league_url = MLB_STRUCTURE["league_url"]
        self.config = MLB_STRUCTURE

    async def scrape_league_standings(self) -> ScrapeResult:
        try:
            full_url = f"{self.base_url}{self.league_url}"
            await self.navigate_to_url(full_url, wait_for_selector="table#teams_standard_batting")

            batting_stats = await self.extract_table_data("table#teams_standard_batting")
            pitching_stats = await self.extract_table_data("table#teams_standard_pitching")
            team_links = await self.extract_links(self.config["css_selectors"]["team_links"], self.base_url)

            return ScrapeResult(
                sport="MLB", data_type="standings",
                data=[{"batting": batting_stats, "pitching": pitching_stats, "team_urls": team_links}],
                timestamp=datetime.now(), success=True
            )
        except Exception as e:
            logger.error(f"MLB standings error: {e}")
            return ScrapeResult(sport="MLB", data_type="standings", data=[], timestamp=datetime.now(), success=False, error_message=str(e))

    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table")
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            batting = await self.extract_table_data("table#team_batting")
            pitching = await self.extract_table_data("table#team_pitching")

            for row in batting:
                row['team'] = team_name
                row['season'] = '2024'
            for row in pitching:
                row['team'] = team_name
                row['season'] = '2024'

            logger.info(f"✅ MLB team stats successful for {team_name}: {len(batting)} batting, {len(pitching)} pitching")
            return ScrapeResult(
                sport="MLB",
                data_type="team_stats",
                data=[{"batting": batting, "pitching": pitching}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"MLB team stats timeout for {team_url}: {e}")
            else:
                logger.error(f"MLB team stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="MLB",
                data_type="team_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )

    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        try:
            await self.navigate_to_url(team_url, wait_for_selector="table#team_batting")
            await asyncio.sleep(2)

            team_name = await self.page.evaluate("""
                () => {
                    const title = document.querySelector('h1')?.textContent || '';
                    return title.split(' 2024')[0].trim();
                }
            """)

            batters = await self.extract_table_data("table#team_batting")
            pitchers = await self.extract_table_data("table#team_pitching")

            for player in batters:
                player['team'] = team_name
                player['season'] = '2024'
            for player in pitchers:
                player['team'] = team_name
                player['season'] = '2024'

            logger.info(f"✅ MLB player stats successful for {team_name}: {len(batters)} batters, {len(pitchers)} pitchers")
            return ScrapeResult(
                sport="MLB",
                data_type="player_stats",
                data=[{"batters": batters, "pitchers": pitchers}],
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.warning(f"MLB player stats timeout for {team_url}: {e}")
            else:
                logger.error(f"MLB player stats error for {team_url}: {e}")

            return ScrapeResult(
                sport="MLB",
                data_type="player_stats",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=error_msg
            )
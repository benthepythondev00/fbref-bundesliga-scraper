"""
Stathead Premium Scraper - Sports-Reference.com
Scrapes premium statistics data with authentication
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from base_scraper import BaseScraper, ScrapeResult, RateLimiter
import logging

# Load .env file if it exists
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass

logger = logging.getLogger(__name__)

class StatheadScraper(BaseScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.base_url = "https://stathead.com"
        self.login_url = f"{self.base_url}/users/login.cgi"
        self.is_authenticated = False

    async def authenticate(self) -> bool:
        try:
            await self.navigate_to_url(self.login_url)

            username = os.getenv('STATHEAD_USERNAME', 'R3dn4x')
            password = os.getenv('STATHEAD_PASSWORD', 'BenScrape5r')

            if not username or not password:
                logger.error("Stathead credentials not found in environment variables")
                return False

            await self.page.fill('input[name="username"]', username)
            await self.page.fill('input[name="password"]', password)

            await self.page.click('input[type="submit"]')

            await self.page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)

            if "Welcome" in await self.page.content():
                self.is_authenticated = True
                logger.info("Successfully authenticated with Stathead")
                return True
            else:
                logger.error("Stathead authentication failed")
                return False

        except Exception as e:
            logger.error(f"Error during Stathead authentication: {e}")
            return False

    async def extract_stathead_table_data(self, url: str, sport: str, data_type: str) -> ScrapeResult:
        try:
            if not self.is_authenticated:
                auth_result = await self.authenticate()
                if not auth_result:
                    return ScrapeResult(
                        sport=sport,
                        data_type=data_type,
                        data=[],
                        timestamp=datetime.now(),
                        success=False,
                        error_message="Authentication failed"
                    )

            await self.navigate_to_url(url, wait_for_selector="table#stats")

            table_data = await self.page.evaluate("""
                () => {
                    const table = document.querySelector('table#stats');
                    if (!table) return [];

                    const headers = Array.from(table.querySelectorAll('thead th')).map(th => {
                        return th.getAttribute('data-stat') || th.textContent.trim();
                    });

                    const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
                        const cells = Array.from(row.querySelectorAll('td, th'));
                        const rowData = {};

                        cells.forEach((cell) => {
                            const stat = cell.getAttribute('data-stat');
                            if (stat) {
                                rowData[stat] = cell.textContent.trim();
                            }
                        });

                        return rowData;
                    });

                    return rows.filter(row => Object.keys(row).length > 0);
                }
            """)

            logger.info(f"Extracted {len(table_data)} rows from Stathead {sport} {data_type}")

            return ScrapeResult(
                sport=f"Stathead {sport}",
                data_type=data_type,
                data=table_data,
                timestamp=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"Error extracting Stathead data: {e}")
            return ScrapeResult(
                sport=f"Stathead {sport}",
                data_type=data_type,
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

class StatheadBaseballScraper(StatheadScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.batting_url = "https://stathead.com/tiny/Vg8kL"
        self.pitching_url = "https://stathead.com/tiny/VdYZA"

    async def scrape_league_standings(self) -> ScrapeResult:
        return await self.extract_stathead_table_data(self.batting_url, "Baseball", "team_batting")

    async def scrape_team_stats(self, team_url: str = None) -> ScrapeResult:
        return await self.extract_stathead_table_data(self.pitching_url, "Baseball", "team_pitching")

    async def scrape_player_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead Baseball", "player_stats", [], datetime.now(), True)

class StatheadBasketballScraper(StatheadScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.url = "https://stathead.com/tiny/Ofmse"

    async def scrape_league_standings(self) -> ScrapeResult:
        return await self.extract_stathead_table_data(self.url, "Basketball", "team_stats")

    async def scrape_team_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead Basketball", "team_stats", [], datetime.now(), True)

    async def scrape_player_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead Basketball", "player_stats", [], datetime.now(), True)

class StatheadNFLScraper(StatheadScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.url = "https://stathead.com/tiny/SRCmZ"

    async def scrape_league_standings(self) -> ScrapeResult:
        return await self.extract_stathead_table_data(self.url, "NFL", "team_stats")

    async def scrape_team_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead NFL", "team_stats", [], datetime.now(), True)

    async def scrape_player_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead NFL", "player_stats", [], datetime.now(), True)

class StatheadNHLScraper(StatheadScraper):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True):
        super().__init__(rate_limiter, headless)
        self.url = "https://stathead.com/tiny/7BFaR"

    async def scrape_league_standings(self) -> ScrapeResult:
        return await self.extract_stathead_table_data(self.url, "NHL", "team_stats")

    async def scrape_team_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead NHL", "team_stats", [], datetime.now(), True)

    async def scrape_player_stats(self, team_url: str = None) -> ScrapeResult:
        return ScrapeResult("Stathead NHL", "player_stats", [], datetime.now(), True)
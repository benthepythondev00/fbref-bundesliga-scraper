"""
Base Scraper Architecture - Multi-Sport Scraper
Playwright-basierte Scraping-Engine mit Anti-Detection und Rate-Limiting
"""

import asyncio
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapeResult:
    sport: str
    data_type: str
    data: List[Dict[str, Any]]
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60 / requests_per_minute
        self.last_request_time = 0

    async def wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < 0.5:  # Minimal delay - just 0.5 seconds
            wait_time = 0.5 - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

class BaseScraper(ABC):
    def __init__(self, rate_limiter: RateLimiter, headless: bool = True, max_retries: int = 3):
        self.rate_limiter = rate_limiter
        self.headless = headless
        self.max_retries = max_retries
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.processed_teams = set()  # Track which teams we've successfully processed

    async def initialize_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.page = await context.new_page()
        self.page.set_default_timeout(45000)  # Increased timeout to 45 seconds

        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        logger.info(f"{self.__class__.__name__}: Browser initialized")

    async def close_browser(self):
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception as e:
            logger.warning(f"Error closing page: {e}")

        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

        logger.info(f"{self.__class__.__name__}: Browser closed")

    async def restart_browser(self):
        """Restart browser when timeouts or other issues occur."""
        logger.info(f"{self.__class__.__name__}: Restarting browser due to timeout...")
        await self.close_browser()
        await asyncio.sleep(2)  # Brief pause before restart
        await self.initialize_browser()
        logger.info(f"{self.__class__.__name__}: Browser restarted successfully")

    async def navigate_to_url(self, url: str, wait_for_selector: Optional[str] = None, retry_count: int = 0):
        await self.rate_limiter.wait()

        try:
            logger.info(f"Navigating to: {url}")
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # Handle cookie consent popups that block content
            await self._handle_cookie_consent()

            if wait_for_selector:
                await self.page.wait_for_selector(wait_for_selector, timeout=90000)  # 90s timeout for slow pages

            await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            if retry_count < self.max_retries:
                logger.warning(f"Navigation failed (attempt {retry_count + 1}/{self.max_retries + 1}): {e}")
                await self.restart_browser()
                return await self.navigate_to_url(url, wait_for_selector, retry_count + 1)
            else:
                logger.error(f"Navigation failed after {self.max_retries + 1} attempts: {e}")
                raise

    async def _handle_cookie_consent(self):
        """Handle various cookie consent popups that might block page content."""
        try:
            # Wait a moment for any popups to appear
            await asyncio.sleep(1)

            # Common cookie consent selectors - try them all
            consent_selectors = [
                # Sports Reference / Basketball Reference cookie popup
                ".osano-cm-accept-all",
                ".osano-cm-save",
                "button[class*='accept-all']",
                "button[class*='accept']",
                # Generic cookie consent selectors
                "[data-accept-all-cookies]",
                "#CybotCookiebotDialogBodyButtonAccept",
                ".cookie-consent-accept",
                ".cookies-accept",
                ".accept-cookies",
                ".gdpr-accept"
            ]

            for selector in consent_selectors:
                try:
                    # Look for popup button (don't wait long)
                    button = await self.page.wait_for_selector(selector, timeout=2000)
                    if button:
                        logger.info(f"Found cookie consent button: {selector}")
                        await button.click()
                        logger.info("✅ Clicked cookie consent button")
                        await asyncio.sleep(1)  # Wait for popup to dismiss
                        return
                except:
                    # Try next selector
                    continue

            # Try to close any modal dialogs
            close_selectors = [
                ".osano-cm-close",
                "[aria-label*='close']",
                ".modal-close",
                ".close-button"
            ]

            for selector in close_selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=1000)
                    if button:
                        logger.info(f"Found close button: {selector}")
                        await button.click()
                        await asyncio.sleep(1)
                        return
                except:
                    continue

        except Exception as e:
            # Don't fail the whole navigation for cookie popup issues
            logger.debug(f"Cookie consent handling finished: {e}")
            pass

    async def extract_table_data(self, table_selector: str) -> List[Dict[str, Any]]:
        try:
            await self.page.wait_for_selector(table_selector, timeout=10000)
        except Exception as e:
            logger.warning(f"Table {table_selector} not found: {e}")
            return []

        table_data = await self.page.evaluate(f"""
            () => {{
                const table = document.querySelector('{table_selector}');
                if (!table) return [];

                const headers = Array.from(table.querySelectorAll('thead th')).map(th => {{
                    return th.getAttribute('data-stat') || th.textContent.trim();
                }});

                const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {{
                    const cells = Array.from(row.querySelectorAll('td, th'));
                    const rowData = {{}};

                    cells.forEach((cell) => {{
                        const stat = cell.getAttribute('data-stat');
                        if (stat) {{
                            rowData[stat] = cell.textContent.trim();
                        }}
                    }});

                    return rowData;
                }});

                return rows.filter(row => Object.keys(row).length > 0);
            }}
        """)

        logger.info(f"Extracted {len(table_data)} rows from {table_selector}")
        return table_data

    async def extract_links(self, link_selector: str, base_url: str) -> List[str]:
        links = await self.page.evaluate("""
            ({selector, baseUrl}) => {
                const elements = document.querySelectorAll(selector);
                return Array.from(elements).map(el => {
                    const href = el.getAttribute('href');
                    if (href && href.startsWith('http')) return href;
                    if (href) return baseUrl + href;
                    return null;
                }).filter(link => link !== null);
            }
        """, {"selector": link_selector, "baseUrl": base_url})

        unique_links = list(set(links))
        logger.info(f"Found {len(unique_links)} unique links")
        return unique_links

    @abstractmethod
    async def scrape_league_standings(self) -> ScrapeResult:
        pass

    @abstractmethod
    async def scrape_team_stats(self, team_url: str) -> ScrapeResult:
        pass

    @abstractmethod
    async def scrape_player_stats(self, team_url: str) -> ScrapeResult:
        pass

    async def scrape_all(self) -> List[ScrapeResult]:
        results = []
        browser_restart_count = 0
        max_browser_restarts = 5

        try:
            await self.initialize_browser()

            # Scrape league standings with retry logic
            standings = await self._scrape_with_retry(self.scrape_league_standings, "league_standings")
            results.append(standings)

            if standings.success and standings.data and len(standings.data) > 0 and 'team_urls' in standings.data[0]:
                team_urls = standings.data[0]['team_urls']
                total_teams = len(team_urls)
                logger.info(f"Processing {total_teams} teams...")

                for i, team_url in enumerate(team_urls):
                    team_id = self._extract_team_id(team_url)

                    if team_id in self.processed_teams:
                        logger.info(f"Skipping already processed team {i+1}/{total_teams}: {team_id}")
                        continue

                    logger.info(f"Processing team {i+1}/{total_teams}: {team_id}")

                    # Process team stats with retry logic
                    try:
                        team_stats = await self._scrape_team_with_retry(team_url, "team_stats")
                        results.append(team_stats)

                        player_stats = await self._scrape_team_with_retry(team_url, "player_stats")
                        results.append(player_stats)

                        # Mark team as processed only if both operations succeeded
                        if team_stats.success and player_stats.success:
                            self.processed_teams.add(team_id)
                            logger.info(f"✅ Successfully processed team: {team_id}")
                        else:
                            logger.warning(f"⚠️  Partial success for team: {team_id}")

                    except Exception as e:
                        if "timeout" in str(e).lower() and browser_restart_count < max_browser_restarts:
                            logger.warning(f"Global timeout detected, restarting browser ({browser_restart_count + 1}/{max_browser_restarts})")
                            await self.restart_browser()
                            browser_restart_count += 1
                            # Don't increment i, retry this team
                            continue
                        else:
                            logger.error(f"Failed to process team {team_id}: {e}")
                            # Add failed results
                            results.append(ScrapeResult(
                                sport=self.__class__.__name__.replace("Scraper", ""),
                                data_type="team_stats",
                                data=[],
                                timestamp=datetime.now(),
                                success=False,
                                error_message=f"Team stats failed: {str(e)}"
                            ))
                            results.append(ScrapeResult(
                                sport=self.__class__.__name__.replace("Scraper", ""),
                                data_type="player_stats",
                                data=[],
                                timestamp=datetime.now(),
                                success=False,
                                error_message=f"Player stats failed: {str(e)}"
                            ))

                logger.info(f"✅ Completed processing all teams. Processed: {len(self.processed_teams)}/{total_teams}")

        except Exception as e:
            logger.error(f"Critical scraping error: {e}", exc_info=True)
            results.append(ScrapeResult(
                sport=self.__class__.__name__.replace("Scraper", ""),
                data_type="error",
                data=[],
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            ))
        finally:
            await self.close_browser()

        return results

    def _extract_team_id(self, team_url: str) -> str:
        """Extract a unique team identifier from the team URL."""
        try:
            # Extract team identifier from URL - works for most sports reference sites
            if "/teams/" in team_url:
                return team_url.split("/teams/")[1].split("/")[0]
            elif "/squads/" in team_url:
                return team_url.split("/squads/")[1].split("/")[0]
            else:
                return team_url.split("/")[-2]  # Fallback
        except:
            return team_url  # Last resort fallback

    async def _scrape_with_retry(self, scrape_method, operation_name: str):
        """Generic retry wrapper for any scraping method."""
        for attempt in range(self.max_retries + 1):
            try:
                result = await scrape_method()
                if result.success:
                    return result
                elif attempt < self.max_retries:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {operation_name}: {result.error_message}")
                    await self.restart_browser()
                else:
                    logger.error(f"Final attempt failed for {operation_name}: {result.error_message}")
                    return result
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Exception on attempt {attempt + 1}/{self.max_retries + 1} for {operation_name}: {e}")
                    await self.restart_browser()
                else:
                    logger.error(f"Final attempt failed for {operation_name}: {e}")
                    return ScrapeResult(
                        sport=self.__class__.__name__.replace("Scraper", ""),
                        data_type=operation_name,
                        data=[],
                        timestamp=datetime.now(),
                        success=False,
                        error_message=str(e)
                    )

    async def _scrape_team_with_retry(self, team_url: str, operation_type: str):
        """Retry wrapper specifically for team-based operations."""
        for attempt in range(self.max_retries + 1):
            try:
                if operation_type == "team_stats":
                    result = await self.scrape_team_stats(team_url)
                elif operation_type == "player_stats":
                    result = await self.scrape_player_stats(team_url)
                else:
                    raise ValueError(f"Unknown operation type: {operation_type}")

                if result.success:
                    return result
                elif attempt < self.max_retries:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {operation_type} on {team_url}: {result.error_message}")
                    await self.restart_browser()
                else:
                    logger.error(f"Final attempt failed for {operation_type} on {team_url}: {result.error_message}")
                    return result

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Exception on attempt {attempt + 1}/{self.max_retries + 1} for {operation_type} on {team_url}: {e}")
                    await self.restart_browser()
                else:
                    logger.error(f"Final attempt failed for {operation_type} on {team_url}: {e}")
                    return ScrapeResult(
                        sport=self.__class__.__name__.replace("Scraper", ""),
                        data_type=operation_type,
                        data=[],
                        timestamp=datetime.now(),
                        success=False,
                        error_message=str(e)
                    )
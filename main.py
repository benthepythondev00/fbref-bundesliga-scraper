"""
Multi-Sport Scraper - Main Orchestrator
Scrapes Bundesliga, NFL, NBA, NHL, MLB and exports to Excel
Enhanced with Stathead premium data integration

Usage:
    python main.py
    python main.py --sports bundesliga nfl
    python main.py --stathead
    python main.py --sports nfl --stathead
    python main.py --headless False
    python main.py --output custom_stats.xlsx
"""

import asyncio
import argparse
import sys
import os
from bundesliga_scraper import BundesligaScraper
from nfl_scraper import NFLScraper
from nba_nhl_mlb_scrapers import NBAScraper, NHLScraper, MLBScraper
from stathead_scraper import StatheadBaseballScraper, StatheadBasketballScraper, StatheadNFLScraper, StatheadNHLScraper
from excel_exporter import ExcelExporter
from base_scraper import RateLimiter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

AVAILABLE_SCRAPERS = {
    "bundesliga": BundesligaScraper,
    "nfl": NFLScraper,
    "nba": NBAScraper,
    "nhl": NHLScraper,
    "mlb": MLBScraper
}

STATHEAD_SCRAPERS = {
    "baseball": StatheadBaseballScraper,
    "basketball": StatheadBasketballScraper,
    "nfl": StatheadNFLScraper,
    "nhl": StatheadNHLScraper
}

async def scrape_sport(scraper_class, rate_limiter, headless):
    scraper = scraper_class(rate_limiter, headless)
    logger.info(f"\n{'='*60}\nStarting {scraper_class.__name__}\n{'='*60}")

    results = await scraper.scrape_all()

    logger.info(f"\n{scraper_class.__name__} completed: {len(results)} results")
    return results

async def scrape_stathead_sport(scraper_class, rate_limiter, headless):
    scraper = scraper_class(rate_limiter, headless)
    logger.info(f"\n{'='*60}\nStarting Stathead {scraper_class.__name__}\n{'='*60}")

    results = []
    try:
        await scraper.initialize_browser()

        standings_result = await scraper.scrape_league_standings()
        results.append(standings_result)

        team_stats_result = await scraper.scrape_team_stats()
        if team_stats_result.success and team_stats_result.data:
            results.append(team_stats_result)

    except Exception as e:
        logger.error(f"Error in Stathead {scraper_class.__name__}: {e}")
    finally:
        await scraper.close_browser()

    logger.info(f"\nStathead {scraper_class.__name__} completed: {len(results)} results")
    return results

async def main():
    parser = argparse.ArgumentParser(description='Multi-Sport Web Scraper with Stathead Integration')
    parser.add_argument('--sports', nargs='+', default=list(AVAILABLE_SCRAPERS.keys()),
                        choices=list(AVAILABLE_SCRAPERS.keys()),
                        help='Sports to scrape (default: all)')
    parser.add_argument('--stathead', action='store_true',
                        help='Include Stathead premium data (requires credentials)')
    parser.add_argument('--headless', type=str, default='True',
                        help='Run browser in headless mode (default: True)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output Excel filename')
    parser.add_argument('--rate-limit', type=int, default=10,
                        help='Requests per minute (default: 10)')

    args = parser.parse_args()

    headless = args.headless.lower() == 'true'
    rate_limiter = RateLimiter(requests_per_minute=args.rate_limit)

    logger.info(f"\n{'='*80}")
    logger.info(f"MULTI-SPORT SCRAPER STARTING")
    logger.info(f"Sports: {', '.join(args.sports)}")
    logger.info(f"Stathead: {args.stathead}")
    logger.info(f"Headless: {headless}")
    logger.info(f"Rate Limit: {args.rate_limit} req/min")
    logger.info(f"{'='*80}\n")

    all_results = []

    # Scrape regular sports data
    for sport in args.sports:
        scraper_class = AVAILABLE_SCRAPERS[sport]
        try:
            results = await scrape_sport(scraper_class, rate_limiter, headless)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error scraping {sport}: {e}", exc_info=True)

    # Scrape Stathead premium data if requested
    if args.stathead:
        if not os.getenv('STATHEAD_USERNAME') or not os.getenv('STATHEAD_PASSWORD'):
            logger.warning("Stathead credentials not found in environment variables")
            logger.info("Set STATHEAD_USERNAME and STATHEAD_PASSWORD or use default credentials")

        for sport_name, scraper_class in STATHEAD_SCRAPERS.items():
            try:
                results = await scrape_stathead_sport(scraper_class, rate_limiter, headless)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error scraping Stathead {sport_name}: {e}", exc_info=True)

    if all_results:
        exporter = ExcelExporter(filename=args.output)
        exporter.export_results(all_results)

        successful_results = [r for r in all_results if r.success]
        failed_results = [r for r in all_results if not r.success]

        logger.info(f"\n{'='*80}")
        logger.info(f"SCRAPING COMPLETED")
        logger.info(f"Total Results: {len(all_results)}")
        logger.info(f"Successful: {len(successful_results)}")
        logger.info(f"Failed: {len(failed_results)}")

        if exporter.filename:
            logger.info(f"Excel File: {exporter.filename}")
        logger.info(f"{'='*80}\n")

        if failed_results:
            logger.warning("\nFailed Results:")
            for result in failed_results:
                logger.warning(f"  - {result.sport} ({result.data_type}): {result.error_message}")
    else:
        logger.error("No results to export")

if __name__ == "__main__":
    asyncio.run(main())
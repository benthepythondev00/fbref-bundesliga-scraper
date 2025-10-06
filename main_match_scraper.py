"""
Main script for Bundesliga Match-by-Match Scraper
Integrates FBRef match scraping with Kicker.de table positions
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from bundesliga_match_scraper import BundesligaMatchScraper
from match_excel_exporter import MatchExcelExporter
from base_scraper import RateLimiter

# Setup logging with safe file handling for Windows
def setup_logging():
    """Setup logging with fallback for permission errors"""
    handlers = [logging.StreamHandler()]

    # Try to create log file in user's home directory or temp directory
    log_paths = [
        Path.cwd() / 'bundesliga_match_scraper.log',  # Current directory
        Path.home() / 'bundesliga_match_scraper.log',  # User home
        Path(os.environ.get('TEMP', '/tmp')) / 'bundesliga_match_scraper.log'  # Temp
    ]

    for log_path in log_paths:
        try:
            # Test if we can write to this location
            log_path.touch(exist_ok=True)
            handlers.append(logging.FileHandler(str(log_path)))
            print(f"📝 Log file: {log_path}")
            break
        except (PermissionError, OSError):
            continue
    else:
        print("⚠️  Warning: Could not create log file (permission denied)")
        print("    Logs will only be shown on screen")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

setup_logging()
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the complete match scraping and Excel export"""

    logger.info("🚀 Starting Bundesliga Match-by-Match Scraper")
    logger.info("=" * 80)

    # Configuration
    rate_limiter = RateLimiter(requests_per_minute=10)
    headless = True  # Set to False for debugging

    try:
        # Initialize the scraper
        scraper = BundesligaMatchScraper(rate_limiter, headless)

        # Run the scraping
        logger.info("📊 Starting match data scraping...")
        results = await scraper.scrape_all()

        if not results or not results[0].success:
            logger.error("❌ Scraping failed!")
            return

        match_data = results[0].data
        logger.info(f"✅ Successfully scraped {len(match_data)} matches")

        # Export to Excel
        logger.info("📝 Exporting data to Excel...")
        exporter = MatchExcelExporter(
            template_path="Vorlage-Scrapen.xlsx",
            output_path=f"Bundesliga_Matches_2024_25_{len(match_data)}_games.xlsx"
        )

        output_file = exporter.export_match_data(match_data)
        logger.info(f"✅ Excel file created: {output_file}")

        # Summary statistics
        logger.info("=" * 80)
        logger.info("📈 SCRAPING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total matches processed: {len(match_data)}")

        # Count successful data extractions
        successful_matches = sum(1 for match in match_data if match.get('home_team_stats') and match.get('away_team_stats'))
        logger.info(f"Matches with complete data: {successful_matches}")

        # Show sample data
        if match_data:
            sample_match = match_data[0]
            logger.info(f"Sample match: {sample_match.get('home_team')} vs {sample_match.get('away_team')}")
            logger.info(f"Matchday: {sample_match.get('matchday')}")
            logger.info(f"Home team position: {sample_match.get('home_team_position')}")
            logger.info(f"Away team position: {sample_match.get('away_team_position')}")

            if sample_match.get('home_team_stats'):
                stats_count = len(sample_match['home_team_stats'])
                logger.info(f"Parameters extracted per team: {stats_count}")

        logger.info("=" * 80)
        logger.info("🎉 Bundesliga Match Scraping Completed Successfully!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Check if venv is activated
    import sys
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected!")
        print("Please activate the virtual environment first:")
        print("source venv/bin/activate")
        sys.exit(1)

    # Run the main function
    asyncio.run(main())
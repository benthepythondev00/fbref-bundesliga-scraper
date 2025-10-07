"""
Debug script to analyze FBRef match page structure
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_match_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("🔍 Navigating to match page...")
        await page.goto('https://fbref.com/en/matches/d42e53df/Monchengladbach-Bayer-Leverkusen-August-23-2024-Bundesliga')

        # Handle cookie consent
        try:
            await page.click('.osano-cm-accept-all', timeout=3000)
            print("✅ Accepted cookies")
        except:
            pass

        # Wait for tables to load
        await asyncio.sleep(8)

        print("\n" + "="*80)
        print("🔍 ANALYZING TABLE STRUCTURE")
        print("="*80 + "\n")

        # Get all table IDs
        table_info = await page.evaluate('''
            () => {
                const tables = document.querySelectorAll('table[id]');
                const info = {};

                tables.forEach(table => {
                    const tableId = table.id;

                    // Get tfoot data
                    const tfoot = table.querySelector('tfoot tr');
                    if (tfoot) {
                        const cells = tfoot.querySelectorAll('th, td');
                        const dataStats = [];

                        cells.forEach(cell => {
                            const dataStat = cell.getAttribute('data-stat');
                            const value = cell.textContent.trim();
                            if (dataStat && dataStat !== 'player') {
                                dataStats.push({
                                    stat: dataStat,
                                    value: value
                                });
                            }
                        });

                        info[tableId] = {
                            tfoot_stats: dataStats,
                            tfoot_count: dataStats.length
                        };
                    }
                });

                return info;
            }
        ''')

        # Print table info
        for table_id, data in table_info.items():
            if 'stats_' in table_id:
                print(f"📊 Table: {table_id}")
                print(f"   Stats count: {data['tfoot_count']}")
                print(f"   First 10 stats:")
                for stat in data['tfoot_stats'][:10]:
                    print(f"      {stat['stat']}: {stat['value']}")
                print()

        # Check for possession
        print("\n" + "="*80)
        print("🔍 CHECKING FOR POSSESSION")
        print("="*80 + "\n")

        possession_info = await page.evaluate('''
            () => {
                // Check scorebox for possession
                const scorebox = document.querySelector('.scorebox');
                if (scorebox) {
                    const divs = scorebox.querySelectorAll('div');
                    for (let div of divs) {
                        if (div.textContent.includes('Possession')) {
                            return {
                                found: true,
                                location: 'scorebox',
                                html: div.innerHTML
                            };
                        }
                    }
                }

                // Check team stats tables
                const tables = document.querySelectorAll('table[id^="stats_"]');
                for (let table of tables) {
                    const cells = table.querySelectorAll('[data-stat="possession"]');
                    if (cells.length > 0) {
                        const values = [];
                        cells.forEach(cell => values.push(cell.textContent.trim()));
                        return {
                            found: true,
                            location: table.id,
                            values: values
                        };
                    }
                }

                return {found: false};
            }
        ''')

        print(f"Possession found: {possession_info['found']}")
        if possession_info['found']:
            print(f"Location: {possession_info['location']}")
            if 'values' in possession_info:
                print(f"Values: {possession_info['values']}")

        print("\n" + "="*80)
        print("🔍 CHECKING data-stat='blocks' VS data-stat='blocked_shots'")
        print("="*80 + "\n")

        blocks_info = await page.evaluate('''
            () => {
                const info = {blocks: [], blocked_shots: [], blocked_passes: []};

                // Check all tables
                const tables = document.querySelectorAll('table[id^="stats_"]');
                tables.forEach(table => {
                    const tableId = table.id;

                    // Check tfoot
                    const tfoot = table.querySelector('tfoot tr');
                    if (tfoot) {
                        const blocksCell = tfoot.querySelector('[data-stat="blocks"]');
                        const blockedShotsCell = tfoot.querySelector('[data-stat="blocked_shots"]');
                        const blockedPassesCell = tfoot.querySelector('[data-stat="blocked_passes"]');

                        if (blocksCell) {
                            info.blocks.push({
                                table: tableId,
                                value: blocksCell.textContent.trim()
                            });
                        }
                        if (blockedShotsCell) {
                            info.blocked_shots.push({
                                table: tableId,
                                value: blockedShotsCell.textContent.trim()
                            });
                        }
                        if (blockedPassesCell) {
                            info.blocked_passes.push({
                                table: tableId,
                                value: blockedPassesCell.textContent.trim()
                            });
                        }
                    }
                });

                return info;
            }
        ''')

        print("Blocks (data-stat='blocks'):")
        for item in blocks_info['blocks']:
            print(f"   {item['table']}: {item['value']}")

        print("\nBlocked Shots (data-stat='blocked_shots'):")
        for item in blocks_info['blocked_shots']:
            print(f"   {item['table']}: {item['value']}")

        print("\nBlocked Passes (data-stat='blocked_passes'):")
        for item in blocks_info['blocked_passes']:
            print(f"   {item['table']}: {item['value']}")

        input("\n\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_match_page())

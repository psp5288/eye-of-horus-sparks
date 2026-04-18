"""
Crawl4AI research scraper for Eye of Horus: Sparks backtest data.

Scrapes Wikipedia pages and public search-result pages for three events:
  - Astroworld Festival (2021 and general history)
  - Coachella 2023
  - Super Bowl LVIII (2024)

Output: data/research_scraped.json
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── crawl4ai import (handles version differences) ──────────────────────────
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    NEW_API = True
except ImportError:
    from crawl4ai import AsyncWebCrawler
    NEW_API = False

# ── Output path ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = REPO_ROOT / "data" / "research_scraped.json"

# ── URL manifest ───────────────────────────────────────────────────────────
EVENTS = [
    {
        "event_id": "astroworld_2021",
        "event_name": "Astroworld Festival 2021",
        "date": "2021-11-05",
        "urls": [
            {
                "url": "https://en.wikipedia.org/wiki/Astroworld_Festival",
                "source_type": "wikipedia",
                "label": "Wikipedia — Astroworld Festival",
            },
            {
                "url": "https://en.wikipedia.org/wiki/2021_Astroworld_Festival_crowd_crush",
                "source_type": "wikipedia",
                "label": "Wikipedia — 2021 crowd crush incident",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Travis_Scott",
                "source_type": "wikipedia",
                "label": "Wikipedia — Travis Scott (artist context)",
            },
            {
                "url": "https://en.wikipedia.org/wiki/NRG_Park",
                "source_type": "wikipedia",
                "label": "Wikipedia — NRG Park (venue)",
            },
        ],
    },
    {
        "event_id": "coachella_2023",
        "event_name": "Coachella Valley Music and Arts Festival 2023",
        "date": "2023-04-14",
        "urls": [
            {
                "url": "https://en.wikipedia.org/wiki/Coachella_Valley_Music_and_Arts_Festival",
                "source_type": "wikipedia",
                "label": "Wikipedia — Coachella (overview)",
            },
            {
                "url": "https://en.wikipedia.org/wiki/2023_Coachella_Valley_Music_and_Arts_Festival",
                "source_type": "wikipedia",
                "label": "Wikipedia — Coachella 2023 edition",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Empire_Polo_Club",
                "source_type": "wikipedia",
                "label": "Wikipedia — Empire Polo Club (venue)",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Bad_Bunny",
                "source_type": "wikipedia",
                "label": "Wikipedia — Bad Bunny (headliner context)",
            },
        ],
    },
    {
        "event_id": "superbowl_lviii",
        "event_name": "Super Bowl LVIII",
        "date": "2024-02-11",
        "urls": [
            {
                "url": "https://en.wikipedia.org/wiki/Super_Bowl_LVIII",
                "source_type": "wikipedia",
                "label": "Wikipedia — Super Bowl LVIII",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Allegiant_Stadium",
                "source_type": "wikipedia",
                "label": "Wikipedia — Allegiant Stadium (venue)",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Super_Bowl",
                "source_type": "wikipedia",
                "label": "Wikipedia — Super Bowl (overview + attendance history)",
            },
            {
                "url": "https://en.wikipedia.org/wiki/Kansas_City_Chiefs",
                "source_type": "wikipedia",
                "label": "Wikipedia — Kansas City Chiefs (participant context)",
            },
        ],
    },
]


async def scrape_url(
    crawler: "AsyncWebCrawler",
    url: str,
    source_type: str,
    label: str,
) -> dict:
    """
    Scrape a single URL and return a structured result dict.

    Parameters
    ----------
    crawler : AsyncWebCrawler
        Shared crawler instance.
    url : str
        Target URL.
    source_type : str
        One of: wikipedia | news | search.
    label : str
        Human-readable description of the source.

    Returns
    -------
    dict
        url, source_type, label, content_length, content_preview,
        full_content, scraped_at, status, error (if any).
    """
    scraped_at = datetime.now(timezone.utc).isoformat()
    print(f"  Scraping: {label[:60]}")

    try:
        if NEW_API:
            config = CrawlerRunConfig(
                word_count_threshold=100,
                cache_mode=CacheMode.BYPASS,
                page_timeout=30000,
            )
            result = await crawler.arun(url=url, config=config)
        else:
            result = await crawler.arun(
                url=url,
                word_count_threshold=100,
                bypass_cache=True,
            )

        if result.success and result.markdown:
            content = result.markdown.strip()
            return {
                "url": url,
                "source_type": source_type,
                "label": label,
                "content_length": len(content),
                "content_preview": content[:500],
                "full_content": content[:8000],  # cap at 8k chars per source
                "scraped_at": scraped_at,
                "status": "success",
            }
        else:
            return {
                "url": url,
                "source_type": source_type,
                "label": label,
                "content_length": 0,
                "content_preview": "",
                "full_content": "",
                "scraped_at": scraped_at,
                "status": "error",
                "error": "No markdown content returned",
            }

    except Exception as exc:
        print(f"    ✗ Failed: {exc}")
        return {
            "url": url,
            "source_type": source_type,
            "label": label,
            "content_length": 0,
            "content_preview": "",
            "full_content": "",
            "scraped_at": scraped_at,
            "status": "error",
            "error": str(exc),
        }


async def run_scraper() -> dict:
    """
    Run the full scrape across all events and return the output JSON structure.

    Returns
    -------
    dict
        Full output structure with scraped_at, events, and summary.
    """
    print("\n𓂀 Eye of Horus: Sparks — Crawl4AI Research Scraper")
    print("=" * 55)

    started_at = datetime.now(timezone.utc).isoformat()
    events_output = []
    total_success = 0
    total_error = 0

    async with AsyncWebCrawler(verbose=False) as crawler:
        for event in EVENTS:
            print(f"\n[{event['event_id']}] {event['event_name']}")
            sources = []

            for source in event["urls"]:
                result = await scrape_url(
                    crawler=crawler,
                    url=source["url"],
                    source_type=source["source_type"],
                    label=source["label"],
                )
                sources.append(result)

                if result["status"] == "success":
                    total_success += 1
                    print(f"    ✓ {result['content_length']:,} chars")
                else:
                    total_error += 1

                # Polite delay between requests
                await asyncio.sleep(1.0)

            events_output.append(
                {
                    "event_id": event["event_id"],
                    "event_name": event["event_name"],
                    "date": event["date"],
                    "sources": sources,
                }
            )

    total_urls = total_success + total_error
    output = {
        "scraped_at": started_at,
        "total_urls": total_urls,
        "events": events_output,
        "summary": {
            "total_urls_scraped": total_urls,
            "successful": total_success,
            "failed": total_error,
            "success_rate_pct": round(total_success / max(total_urls, 1) * 100, 1),
        },
    }

    return output


def save_results(output: dict) -> Path:
    """
    Save the scrape results to data/research_scraped.json.

    Parameters
    ----------
    output : dict
        Full output from run_scraper().

    Returns
    -------
    Path
        Absolute path to the saved file.
    """
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    return OUTPUT_FILE


if __name__ == "__main__":
    output = asyncio.run(run_scraper())
    saved_path = save_results(output)

    summary = output["summary"]
    print(f"\n{'=' * 55}")
    print(f"✓ Scraping complete")
    print(f"  URLs attempted : {summary['total_urls_scraped']}")
    print(f"  Successful     : {summary['successful']}")
    print(f"  Failed         : {summary['failed']}")
    print(f"  Success rate   : {summary['success_rate_pct']}%")
    size_kb = saved_path.stat().st_size / 1024
    print(f"  Output file    : {saved_path}")
    print(f"  File size      : {size_kb:.1f} KB")
    print()

"""
Anthropic Signal Normalization
==============================

This module implements the 'Transformation' phase of the ETL pipeline for 
Anthropic blog articles. It converts raw URLs into high-integrity technical 
markdown using the Docling engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from typing import Dict, Optional

from backend.features.signals.repository import SignalRepository
from backend.features.signals.scrapers.anthropic import AnthropicScraper


def process_anthropic_markdown(limit: Optional[int] = None) -> Dict:
    scraper = AnthropicScraper()
    repo = SignalRepository()

    articles = repo.get_anthropic_articles_without_markdown(limit=limit)
    processed = 0
    failed = 0

    for article in articles:
        markdown = scraper.url_to_markdown(article.url)
        try:
            if markdown:
                repo.update_anthropic_article_markdown(article.guid, markdown)
                processed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"Error processing article {article.guid}: {e}")
            continue

    return {"total": len(articles), "processed": processed, "failed": failed}


if __name__ == "__main__":
    result = process_anthropic_markdown()
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")

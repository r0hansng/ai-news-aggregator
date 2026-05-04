from app.scrapers.openai import OpenAIScraper
from app.scrapers.anthropic import AnthropicScraper
from app.database.repository import Repository

def scrape_all_articles(hours: int = 24):
    repo = Repository()
    
    # 1. Scrape OpenAI
    print(f"Scraping OpenAI (last {hours} hours)...")
    openai = OpenAIScraper()
    openai_articles = openai.get_articles(hours=hours)
    if openai_articles:
        count = repo.bulk_create_openai_articles([a.model_dump() for a in openai_articles])
        print(f"Added {count} new OpenAI articles")
        
    # 2. Scrape Anthropic
    print(f"Scraping Anthropic (last {hours} hours)...")
    anthropic = AnthropicScraper()
    anthropic_articles = anthropic.get_articles(hours=hours)
    if anthropic_articles:
        count = repo.bulk_create_anthropic_articles([a.model_dump() for a in anthropic_articles])
        print(f"Added {count} new Anthropic articles")
        
    return True

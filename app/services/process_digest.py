import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.digest_agent import DigestAgent
from app.database.repository import Repository

def process_digests(limit=None):
    agent = DigestAgent()
    repo = Repository()
    
    articles = repo.get_articles_without_digest(limit=limit)
    total = len(articles)
    processed = 0
    failed = 0
    
    print(f"Starting digest processing for {total} articles")
    
    for idx, article in enumerate(articles, 1):
        article_type = article["type"]
        article_id = article["id"]
        title = article["title"]
        short_title = title[:60] + "..." if len(title) > 60 else title
        
        print(f"[{idx}/{total}] Processing {article_type}: {short_title} (ID: {article_id})")
        
        try:
            digest = agent.generate_digest(
                title=title,
                content=article["content"],
                article_type=article_type
            )
            
            if digest:
                repo.create_digest(
                    article_type=article_type,
                    article_id=article_id,
                    url=article["url"],
                    title=digest.title,
                    summary=digest.summary,
                    published_at=article.get("published_at")
                )
                processed += 1
                print(f"✓ Created digest for {article_type} {article_id}")
            else:
                failed += 1
                print(f"✗ Failed to generate digest for {article_type} {article_id}")
        except Exception as e:
            failed += 1
            print(f"✗ Error processing {article_type} {article_id}: {e}")
    
    print(f"Done: {processed} processed, {failed} failed out of {total}")
    
    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }

if __name__ == "__main__":
    result = process_digests()
    print(f"Total: {result['total']} | Processed: {result['processed']} | Failed: {result['failed']}")


import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.runner import run_scrapers
from app.services.process_anthropic import process_anthropic_markdown
from app.services.process_youtube import process_youtube_transcripts
from app.services.process_digest import process_digests
from app.services.process_email import send_digest_email

def run_daily_pipeline(hours=24, top_n=10):
    start_time = time.time()
    
    print("=" * 50)
    print("Starting Daily AI News Aggregator Pipeline")
    print("=" * 50)
    
    results = {
        "success": False,
        "scraping": {},
        "processing": {},
        "digests": {},
        "email": {}
    }
    
    try:
        print("\n[1/5] Scraping articles...")
        scraped = run_scrapers(hours=hours)
        results["scraping"] = {
            "youtube": len(scraped.get("youtube", [])),
            "openai": len(scraped.get("openai", [])),
            "anthropic": len(scraped.get("anthropic", []))
        }
        print(f"Scraped {results['scraping']['youtube']} YouTube, {results['scraping']['openai']} OpenAI, {results['scraping']['anthropic']} Anthropic")
        
        print("\n[2/5] Processing Anthropic markdown...")
        anthropic_result = process_anthropic_markdown()
        results["processing"]["anthropic"] = anthropic_result
        print(f"Processed {anthropic_result['processed']} Anthropic articles ({anthropic_result['failed']} failed)")
        
        print("\n[3/5] Processing YouTube transcripts...")
        yt_result = process_youtube_transcripts()
        results["processing"]["youtube"] = yt_result
        print(f"Processed {yt_result['processed']} transcripts ({yt_result['unavailable']} unavailable)")
        
        print("\n[4/5] Creating digests...")
        digest_result = process_digests()
        results["digests"] = digest_result
        print(f"Created {digest_result['processed']} digests ({digest_result['failed']} failed out of {digest_result['total']})")
        
        print("\n[5/5] Sending email digest...")
        email_result = send_digest_email(hours=hours, top_n=top_n)
        results["email"] = email_result
        
        if email_result["success"]:
            print(f"Email sent with {email_result['articles_count']} articles")
            results["success"] = True
        else:
            print(f"Failed to send email: {email_result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"Pipeline failed: {e}")
        results["error"] = str(e)
    
    duration = time.time() - start_time
    results["duration_seconds"] = duration
    
    print("\n" + "=" * 50)
    print("Pipeline Summary")
    print("=" * 50)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Success: {results['success']}")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    result = run_daily_pipeline(hours=24, top_n=10)
    exit(0 if result["success"] else 1)


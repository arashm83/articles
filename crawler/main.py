from cores.article_manager import *
from cores.db_manager import DbManager, Article, Base, engine
import asyncio
from datetime import datetime, timezone
import time

Base.metadata.create_all(bind=engine)

async def job():
    new_articles = get_articles()
    db = DbManager()
    for title, url in new_articles:
        try:
            abstract, pdf_url = await get_article_details(url)
        except Exception as e:
            print(f"Error fetching article details for {url}: {e}")
            continue
        article = Article(title=title, abstract=abstract, url=url, pdf_url=pdf_url, create_at=datetime.now(timezone.utc))
        success = db.add_article(article)
        if success:
            try:
                requests.post('http://0.0.0.0:8000/article', headers={'title': title})
            except Exception as e:
                print(e)
            print('article saved to db:', title)
            with open('visited.txt', 'a') as f:
                f.write(url + '\n')

if __name__ == "__main__":
    
    asyncio.run(job())
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.async_api import async_playwright
import requests


BASE_URL = 'https://physics.aps.org'

with open('visited.txt', 'a') as f:
    f.write('')

visited = set()

with open('visited.txt', 'r') as f:
    for line in f:
        visited.add(line.strip())

def get_articles():
    i = 1
    result = []
    print('getting new articles')
    while True:
        print(f'sending req to https://physics.aps.org/browse/json?page={i}&per_page=5&sort=recent')
        res = requests.get(f'https://physics.aps.org/browse/json?page={i}&per_page=5&sort=recent')
        print('req sent')
        data = res.json().get('hits')
        for article in data:
            url = urljoin(BASE_URL, article['link'])
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            article = soup.find('div', class_='link-list-item')
        
            if article:
                url = article.h4.a.get('href')
                res = requests.get(url, allow_redirects=True)
                article_url = res.url
                if article_url in visited:
                    break
                article_title = article.h4.a.get_text(strip=True)
                print(f'found new article {article_title}')
                result.append((article_title, article_url))
            else:
                pass
        i += 1
        if len(result) >= 5:
            break
    return result


async def get_article_details(url):
    print(f'getting article details {url}')
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until='domcontentloaded', timeout=20000)
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        pdf_url = urljoin('https://journals.aps.org', soup.find('div', class_='right').a.get('href'))
        abstract = soup.find('div', class_='content', id='abstract-section-content').p.get_text(strip=True)
        await browser.close()
        return abstract, pdf_url
        

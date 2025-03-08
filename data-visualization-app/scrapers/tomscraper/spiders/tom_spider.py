import scrapy
import re
import json
from tomscraper.itemloaders import TomArticleLoader
from tomscraper.items import TomArticle
import logging
import psycopg2
from dateutil import parser
import pytz
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace('www.', '')
    normalized_url = urlunparse(parsed_url._replace(netloc=netloc))
    return normalized_url

def normalize_date(date_str):
    """
    Converts various date formats into a consistent ISO 8601 format with UTC timezone.
    """
    try:
        parsed_date = parser.parse(date_str)

        # Convert to UTC timezone (to avoid inconsistencies)
        parsed_date = parsed_date.astimezone(pytz.UTC)

        # Format as ISO 8601 before inserting into DB
        return parsed_date.strftime('%Y-%m-%dT%H:%M:%S%z')  # Example: '2025-02-26T18:42:00+0000'
    
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str}, {e}")
        return None


class TomSpiderSpider(scrapy.Spider):

    name = "tom_spider"
    allowed_domains = ["timesofmalta.com"]
    start_urls = ["https://timesofmalta.com/news/national"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'referer': 'https://www.timesofmalta.com/'})

    def __init__(self, *args, **kwargs):
        super(TomSpiderSpider, self).__init__(*args, **kwargs)
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        try:
            body = response.body.decode('utf-8')
        except UnicodeDecodeError:
            self.logger.error("Failed to decode response body with utf-8 encoding")
            return

        articles = re.findall(r'<script type=.application.ld.json. id=.listing-ld.>{.@graph.:(.+?),.@context.:.http:..schema.org..<.script>', body, re.S)
        
        jsonArticles = json.loads(''.join(articles))
        
        for article in jsonArticles:
            articleLoader = TomArticleLoader(item=TomArticle(), selector=article)

            # 🔥 Normalize the date before adding it to the loader
            normalized_date = normalize_date(article['datePublished'])

            if normalized_date:
                articleLoader.add_value('datePublished', normalized_date)
            else:
                self.logger.warning(f"Skipping article due to invalid date: {article['datePublished']}")
                continue  # Skip articles with invalid dates

            articleLoader.add_value('articleSection', article['articleSection'])
            articleLoader.add_value('author', article['author'][0]['name'])
            articleLoader.add_value('headline', article['headline'])

            # Normalize the URL
            article_url = normalize_url(article['url'])
            articleLoader.add_value('link', article['url'])

            # article_url = article['url']

            # ✅ Check if the article already exists in the database
            self.cursor.execute("SELECT 1 FROM articles WHERE link = %s", (article_url,))
            if not self.cursor.fetchone():
                logging.debug(f"🆕 New article, fetching content: {article_url}")
                yield scrapy.Request(article_url, callback=self.parse_article, meta={'loader': articleLoader})
            else:
                logging.debug(f"✅ Article already exists: {article_url}")

    def parse_article(self, response):
        articleLoader = response.meta['loader']
        article_content = ' '.join(response.css('article p::text').getall()).strip()  # Update the selector to match the actual content
        logging.debug(f"Extracted article content: {article_content}")  # Add debug statement
        articleLoader.add_value('content', article_content)
        articleLoader.add_value('agency', 'ToM')  # Set the agency field
        yield articleLoader.load_item()

    def close(self, reason):
        self.cursor.close()
        self.connection.close()
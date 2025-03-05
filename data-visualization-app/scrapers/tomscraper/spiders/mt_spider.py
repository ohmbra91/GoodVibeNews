import scrapy
import re
import json
from tomscraper.itemloaders import TomArticleLoader
from tomscraper.items import TomArticle
import logging
import psycopg2
from dateutil import parser
import pytz

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

class MaltaTodaySpider(scrapy.Spider):
    name = "mt_spider"
    allowed_domains = ["maltatoday.com.mt"]
    start_urls = ["https://www.maltatoday.com.mt/news/national"]

    def __init__(self, *args, **kwargs):
        super(MaltaTodaySpider, self).__init__(*args, **kwargs)
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        # Extract article URLs from the list page
        article_links = response.css('div.article.list-article a::attr(href)').getall()
        for link in article_links:
            article_url = response.urljoin(link)
            # Check if the article already exists in the database
            self.cursor.execute("SELECT 1 FROM articles WHERE link = %s", (article_url,))
            if not self.cursor.fetchone():
                logging.debug(f"Article not found in database, fetching content: {article_url}")
                yield scrapy.Request(article_url, callback=self.parse_article)
            else:
                logging.debug(f"Article already exists in database: {article_url}")

    def parse_article(self, response):
        articleLoader = TomArticleLoader(item=TomArticle(), response=response)

        # Extract and normalize date
        raw_date = response.css('div.article-meta span.date::text').get()
        normalized_date = normalize_date(raw_date) if raw_date else None
        articleLoader.add_value('datePublished', normalized_date)

        # Extract other fields
        articleLoader.add_css('headline', 'div.article-heading h1::text')
        articleLoader.add_css('author', 'div.article-meta span.name::text')
        articleLoader.add_css('link', 'link[rel="canonical"]::attr(href)')
        articleLoader.add_value('link', response.url)
        articleLoader.add_value('agency', 'MT')  # Set the agency field

        # Extract and clean content
        paragraphs = response.css('div.full-article div.content p::text').getall()
        content = ' '.join(paragraphs).replace('\n', ' ').replace('\r', ' ')
        articleLoader.add_value('content', content)

        # Handle missing articleSection
        article_section = response.css('div.article-meta span.section::text').get()
        articleLoader.add_value('articleSection', article_section if article_section else None)

        logging.debug(f"Extracted article content: {articleLoader.get_output_value('content')}")
        yield articleLoader.load_item()

    def close(self, reason):
        self.cursor.close()
        self.connection.close()
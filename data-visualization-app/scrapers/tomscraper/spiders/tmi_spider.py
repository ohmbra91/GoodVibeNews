import scrapy
import re
import json
import logging
import psycopg2
from tomscraper.itemloaders import TomArticleLoader
from tomscraper.items import TomArticle
import random
from scrapy.utils.response import get_base_url
from urllib.parse import urljoin
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
    
class MaltaIndependentSpider(scrapy.Spider):
    name = "tmi_spider"
    allowed_domains = ["independent.com.mt"]
    start_urls = ["https://www.independent.com.mt/local"]

    def __init__(self, *args, **kwargs):
        super(MaltaIndependentSpider, self).__init__(*args, **kwargs)
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        # Extract article URLs from the list page
        article_links = response.css('article.entry-wrapper a::attr(href)').getall()
        for link in article_links:
            article_url = response.urljoin(link)
            # Check if the article already exists in the database
            self.cursor.execute("SELECT 1 FROM articles WHERE link = %s", (article_url,))
            if not self.cursor.fetchone():
                logging.debug(f"Article not found in database, fetching content: {article_url}")
                yield scrapy.Request(article_url, callback=self.parse_article, errback=self.handle_error)
            else:
                logging.debug(f"Article already exists in database: {article_url}")

    def parse_article(self, response):
        articleLoader = TomArticleLoader(item=TomArticle(), response=response)
        articleLoader.add_css('datePublished', 'span.date-published::text')
        articleLoader.add_css('headline', 'meta[property="og:title"]::attr(content)')
        articleLoader.add_css('author', 'meta[name="author"]::attr(content)')
        articleLoader.add_css('link', 'link[rel="canonical"]::attr(href)')
        articleLoader.add_value('link', response.url)
        articleLoader.add_value('agency', 'TMI')  # Set the agency field
        
        # Handle missing articleSection
        article_section = response.css('meta[property="article:section"]::attr(content)').get()
        if article_section:
            articleLoader.add_value('articleSection', article_section)
        else:
            articleLoader.add_value('articleSection', None)

        # Ensure author field is present
        author = articleLoader.get_output_value('author')
        if not author:
            articleLoader.add_value('author', "TMI")

        # Extract all <p> tags and <br> tags within .text-container and join them into one string
        paragraphs = response.css('.text-container p::text, .text-container p br::text, .text-container p span::text').getall()
        content = ' '.join(paragraphs).replace('\n', ' ').replace('\r', ' ')
        articleLoader.add_value('content', content)

        #content = articleLoader.get_output_value('content')
        if not content:
            logging.warning(f"Content missing for article: {response.url}")
            return

        logging.debug(f"Extracted article content: {content}")
        yield articleLoader.load_item()

    def handle_error(self, failure):
        request = failure.request
        logging.error(f"Request failed with status {failure.value.response.status} for URL: {request.url}")
        # Retry the request with a different User-Agent
        new_request = request.copy()
        new_request.dont_filter = True
        yield new_request

    def close(self, reason):
        self.cursor.close()
        self.connection.close()
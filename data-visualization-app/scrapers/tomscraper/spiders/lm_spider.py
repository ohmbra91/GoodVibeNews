import scrapy
import logging
import psycopg2
from tomscraper.itemloaders import TomArticleLoader
from tomscraper.items import TomArticle
from dateutil import parser
import pytz

def normalize_date(date_str):
    """
    Converts various date formats into a consistent ISO 8601 format with UTC timezone.
    """
    try:
        parsed_date = parser.parse(date_str)
        parsed_date = parsed_date.astimezone(pytz.UTC)
        return parsed_date.strftime('%Y-%m-%dT%H:%M:%S%z')  
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str}, {e}")
        return None

class LovinMaltaSpider(scrapy.Spider):
    name = "lm_spider"
    allowed_domains = ["lovinmalta.com"]
    start_urls = ["https://lovinmalta.com/lifestyle/environment/"]

    def __init__(self, *args, **kwargs):
        super(LovinMaltaSpider, self).__init__(*args, **kwargs)
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        """
        Extracts article links from the Environment category listing page.
        """
        article_links = response.xpath("/html/body/main/div/div/div/ul/li/article/div/div[1]/h3/a/@href").getall()
        for link in article_links:
            article_url = response.urljoin(link)
            # Check if the article already exists in the database
            self.cursor.execute("SELECT 1 FROM articles WHERE link = %s", (article_url,))
            if not self.cursor.fetchone():
                logging.debug(f"🆕 New article found, fetching content: {article_url}")
                yield scrapy.Request(article_url, callback=self.parse_article, errback=self.handle_error)
            else:
                logging.debug(f"✅ Article already exists in database: {article_url}")

    def parse_article(self, response):
        """
        Extracts article details from the article page.
        """
        articleLoader = TomArticleLoader(item=TomArticle(), response=response)

        # Extract details using confirmed working XPath
        headline = response.xpath("/html/body/main/div/article/div[1]/header/h1/text()").get()
        author = response.xpath("/html/body/main/div/article/div[1]/header/div[1]/div/div[2]/p/a/text()").get()
        datetime = response.xpath("//time/text()").get().strip()
        categories = response.xpath("//span[contains(@class, 'category')]/a/text()").getall()

        # Normalize date
        normalized_date = normalize_date(datetime) if datetime else None

        # Add values to loader
        articleLoader.add_value('headline', headline)
        articleLoader.add_value('author', author if author else "Lovin Malta")  # Default if missing
        articleLoader.add_value('datePublished', normalized_date)
        articleLoader.add_value('articleSection', categories)
        articleLoader.add_value('link', response.url)
        articleLoader.add_value('agency', 'Lovin Malta')

        # Extract article content
        paragraphs = response.xpath("//div[contains(@class, 'article-content')]//p/text()").getall()
        content = ' '.join(paragraphs).strip()

        if not content:
            logging.warning(f"⚠️ Content missing for article: {response.url}")
            return
    
        articleLoader.add_value('content', content)
        logging.debug(f"Extracted content: {content[:100]}...")  # Show first 100 chars

        yield articleLoader.load_item()

    def handle_error(self, failure):
        """
        Handles failed requests by retrying with a different User-Agent.
        """
        request = failure.request
        logging.error(f"❌ Request failed with status {failure.value.response.status} for URL: {request.url}")

        # Retry the request with a different User-Agent
        new_request = request.copy()
        new_request.dont_filter = True
        yield new_request

    def close(self, reason):
        """
        Closes the database connection when the spider is done.
        """
        self.cursor.close()
        self.connection.close()

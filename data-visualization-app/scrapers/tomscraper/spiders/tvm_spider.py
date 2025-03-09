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

        # Convert to UTC timezone (to avoid inconsistencies)
        parsed_date = parsed_date.astimezone(pytz.UTC)

        # Format as ISO 8601 before inserting into DB
        return parsed_date.strftime('%Y-%m-%dT%H:%M:%S%z')  # Example: '2025-02-26T18:42:00+0000'
    
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str}, {e}")
        return None
    
class TVMNewsSpider(scrapy.Spider):
    name = "tvm_spider"
    allowed_domains = ["tvmnews.mt"]
    start_urls = ["https://tvmnews.mt/ahbarijiet_category/lokali/"]

    def __init__(self, *args, **kwargs):
        super(TVMNewsSpider, self).__init__(*args, **kwargs)
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        """
        Extracts article links from the news listing page.
        """
        article_links = response.css('h2.penci-entry-title a::attr(href)').getall()
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

        # Extract details
        headline = response.css("h1.post-title.single-post-title.entry-title::text").get()
        author = response.css("span.author-italic a::text").get()
        datetime = response.css("time.entry-date.published::attr(datetime)").get()
        categories = response.css("span.cat a::text").getall()

        # Normalize date
        normalized_date = normalize_date(datetime) if datetime else None
        
        # Convert categories array to a comma-separated string
        categories_str = ', '.join(categories)

        # Add values to loader
        articleLoader.add_value('headline', headline)
        articleLoader.add_value('author', author if author else "TVM News")  # Default if missing
        articleLoader.add_value('datePublished', normalized_date)
        articleLoader.add_value('articleSection', categories_str)
        articleLoader.add_value('link', response.url)
        articleLoader.add_value('agency', 'TVM')

        # Extract article content
        paragraphs = response.css("div.inner-post-entry.entry-content p::text").getall()
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
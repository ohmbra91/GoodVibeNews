import sys
sys.path.append('/home/ubuntu/scrapers/data-visualization-app')
import psycopg2
from itemadapter import ItemAdapter
from flask_socketio import SocketIO
from flask import Flask
import openai
import logging
from shared.database import get_articles  # Import get_articles from shared.database
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_article_analysis(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sentiment analysis and political classification model."},
                {"role": "user", "content": f"""
                Analyze the sentiment of the following news article and assign a score from -100 (very negative) to +100 (very positive). 
                Also, classify whether the article is related to politics or not (yes or no).
                Important: Only send the sentiment score followed by 'yes' or 'no' separated by a comma.\n\n{text}\n\nSentiment score and Political status:\n
                """}
            ]
        )
        logging.debug(f"OpenAI API response: {response}")
        result = response['choices'][0]['message']['content'].strip()
        sentiment_score_str, is_political_str = result.split(',')
        sentiment_score = float(sentiment_score_str.strip())
        is_political = is_political_str.strip().lower() == 'yes'
        return sentiment_score, is_political
    except Exception as e:
        logging.error(f"Error fetching article analysis: {e}")
        return 0.0, False

class SavingToPostgresPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_socketio()

    def create_connection(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="news_scraper_db",
            user="ubuntu",
            password="scrapy"
        )
        self.curr = self.connection.cursor()

    def create_socketio(self):
        app = Flask(__name__)
        self.socketio = SocketIO(app, message_queue='redis://')  # Use a message queue for inter-process communication

    def process_item(self, item, spider):
        sentiment_score, is_political = get_article_analysis(item["content"])  # Add sentiment score and political status to the item
        item["sentiment_score"] = sentiment_score
        item["is_political"] = is_political
        logging.debug(f"Processing item: {item}")  # Add debug statement
        self.store_db(item)
        self.socketio.emit('update_articles', get_articles())  # Emit the updated articles
        return item

    def store_db(self, item):
        try:
            logging.debug(f"Storing item in database: {item}")  # Add debug statement
            self.curr.execute(""" 
                INSERT INTO articles (agency, section, author, date, headline, link, sentiment_score, is_political, content) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (link) DO NOTHING;
            """, (
                item["agency"],
                item.get("articleSection", None),
                item.get("author", None),
                item.get("datePublished"),
                item["headline"],
                item["link"],
                item["sentiment_score"],
                item["is_political"],
                item["content"]
            ))
            self.connection.commit()
            logging.debug(f"Saved article: {item['headline']}")
        except BaseException as e:
            logging.error(f"Error saving article: {e}")

# Example usage of the pipeline
if __name__ == "__main__":
    pipeline = SavingToPostgresPipeline()
    test_item = {
        "agency": "Test Agency",
        "articleSection": "Politics",
        "author": "John Doe",
        "datePublished": "2025-03-08",
        "headline": "Test Headline",
        "link": "http://example.com/test",
        "content": "This is a test article content about politics."
    }
    pipeline.process_item(test_item, spider=None)
import sys
sys.path.append('/home/ubuntu/scrapers/data-visualization-app')

import psycopg2
from itemadapter import ItemAdapter
from flask_socketio import SocketIO
from scrapy.exceptions import DropItem
from flask import Flask
import openai
import logging
from tomscraper.items import TomArticle
from shared.database import get_articles  # Import get_articles from shared.database
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up OpenAI API key
openai.api_key = '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'

def get_sentiment_score(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sentiment analysis model."},
                {"role": "user", "content": f""""
                 Analyze the sentiment of the following news article and assign a score from -100 (very negative) to +100 (very positive). 
                 Consider factors such as environmental impact, legal fairness, and public interest. 
                 Important to only send a number.\n\n{text}\n\nSentiment score:
                 """}
            ]
        )
        logging.debug(f"OpenAI API response: {response}")
        sentiment_score_str = response['choices'][0]['message']['content']
        sentiment_score = float(sentiment_score_str.strip())
        return sentiment_score
    except Exception as e:
        logging.error(f"Error fetching sentiment score: {e}")
        return 0.0

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
        item["sentiment_score"] = get_sentiment_score(item["content"])  # Add sentiment score to the item
        logging.debug(f"Processing item: {item}")  # Add debug statement
        self.store_db(item)
        self.socketio.emit('update_articles', get_articles())  # Emit the updated articles
        return item

    def store_db(self, item):
        try:
            logging.debug(f"Storing item in database: {item}")  # Add debug statement
            self.curr.execute(""" 
                INSERT INTO articles (agency, section, author, date, headline, link, sentiment_score, content) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (link) DO NOTHING;
            """, (
                item["agency"],
                item.get("articleSection", None),
                item.get("author", None),
                item.get("datePublished"),
                item["headline"],
                item["link"],
                item["sentiment_score"],
                item["content"]
            ))
            self.connection.commit()
            logging.debug(f"Saved article: {item['headline']}")
        except BaseException as e:
            logging.error(f"Error saving article: {e}")
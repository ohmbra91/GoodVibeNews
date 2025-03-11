import os
import sys
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
#from flask_socketio import SocketIO
import psycopg2
import logging

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import get_articles, update_articles  # Import get_articles and update_articles from shared.database

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# def emit_update_articles():
#     articles = get_articles()
#     socketio.emit('update_articles', articles)
#     logging.debug("Emitted update_articles event")
#     print("Real-time update sent to clients!")

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app, resources={r"/*": {"origins": ["https://goodvibenews.live", "http://13.60.225.221:3000", "http://localhost:3000"]}}) # Allow both domain and IP address
#socketio = SocketIO(app, cors_allowed_origins=["https://goodvibenews.live", "http://13.60.225.221:3000", "http://localhost:3000"]) # Allow both domain and IP address

@app.route('/', defaults={"path": ""})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route('/api/articles', methods=['GET'])
def articles():
    articles = get_articles()
    logging.debug(f"Fetched articles: {articles}")  # Add debug statement
    return jsonify(articles)

# @app.route("/trigger_update", methods=["POST"])
# def trigger_update():
#     """Manually trigger an update for testing."""
#     emit_update_articles()
#     return jsonify({"message": "Update triggered"}), 200

# @app.route("/update_articles", methods=["POST"])
# def update_articles_route():
#     """Endpoint to update articles and emit updates."""
#     update_articles()  # Update articles in the database or fetch new articles
#     emit_update_articles()  # Emit the updated articles to WebSocket clients
#     return jsonify({"message": "Articles updated and emitted"}), 200

@app.route("/api/visitor_count", methods=["GET"])
def get_visitor_count():
    conn = psycopg2.connect(database="news_scraper_db", user="ubuntu", password="scrapy", host="127.0.0.1", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM visitors WHERE id = 1")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({"count": count})

@app.route("/api/increment_visitor_count", methods=["POST"])
def increment_visitor_count():
    conn = psycopg2.connect(database="news_scraper_db", user="ubuntu", password="scrapy", host="127.0.0.1", port="5432")
    cursor = conn.cursor()
    cursor.execute("UPDATE visitors SET count = count + 1 WHERE id = 1")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Visitor count incremented"}), 200

if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

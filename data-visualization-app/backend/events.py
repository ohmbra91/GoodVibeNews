from flask_socketio import emit
from shared.database import get_articles

def send_articles():
    articles = get_articles()
    emit('update_articles', articles, broadcast=True)
import psycopg2

def get_articles():
    connection = psycopg2.connect(
        host="localhost",
        database="news_scraper_db",
        user="ubuntu",
        password="scrapy"
    )
    cursor = connection.cursor()

    # ✅ Fetch articles sorted by date in DESC order (latest first)
    cursor.execute("SELECT agency, section, author, date, headline, link, sentiment_score, content FROM articles ORDER BY date DESC")

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    articles = []
    for row in rows:
        articles.append({
            "agency": row[0],
            "section": row[1],
            "author": row[2],
            "datePublished": row[3].isoformat() if row[3] else None,  # Convert to ISO 8601
            "headline": row[4],
            "link": row[5],
            "sentiment_score": row[6],
            "content": row[7]
        })
    return articles

def update_articles():
    connection = psycopg2.connect(
        host="localhost",
        database="news_scraper_db",
        user="ubuntu",
        password="scrapy"
    )
    cursor = connection.cursor()
    # Example update query - replace with your actual update logic
    cursor.execute("UPDATE articles SET sentiment_score = sentiment_score + 1 WHERE sentiment_score < 0")
    connection.commit()
    cursor.close()
    connection.close()
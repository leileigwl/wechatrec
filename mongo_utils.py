import pymongo
import os
from datetime import datetime
import json

# MongoDB connection settings
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/')
DB_NAME = os.environ.get('MONGO_DB', 'wechat_articles')

# Collection names
ARTICLES_COLLECTION = 'articles'
LOGS_COLLECTION = 'logs'

# Connect to MongoDB
def get_db_connection():
    """Get MongoDB connection"""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

# Save article data to MongoDB
def save_article_data(article_data):
    """Save article data to MongoDB"""
    db = get_db_connection()
    
    # Add timestamp for when we received the data
    article_data['saved_at'] = datetime.now().isoformat()
    
    # For each article in the data list
    for article in article_data.get('data', []):
        # Convert publication time to datetime
        if 'pub_time' in article:
            try:
                pub_time = int(article['pub_time'])
                article['pub_time_iso'] = datetime.fromtimestamp(pub_time).isoformat()
            except (ValueError, TypeError):
                pass
                
        # Generate a unique ID based on URL or biz+mid if available
        if 'url' in article:
            article['_id'] = article.get('biz', '') + '_' + article.get('pub_time', '') + '_' + article.get('title', '')[:50]
    
    # Insert the original request data as a record
    try:
        db[ARTICLES_COLLECTION].insert_one(article_data)
        return True
    except pymongo.errors.DuplicateKeyError:
        # Update existing record
        db[ARTICLES_COLLECTION].update_one(
            {'_id': article_data.get('_id')},
            {'$set': article_data}
        )
        return True
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return False

# Save log data to MongoDB
def save_log(log_data):
    """Save log entry to MongoDB"""
    db = get_db_connection()
    
    try:
        db[LOGS_COLLECTION].insert_one(log_data)
        return True
    except Exception as e:
        print(f"Error saving log to MongoDB: {e}")
        return False

# Get articles from MongoDB
def get_articles(limit=100, skip=0, query=None):
    """Get articles from MongoDB with pagination"""
    db = get_db_connection()
    
    if query is None:
        query = {}
        
    try:
        cursor = db[ARTICLES_COLLECTION].find(query).sort('stamp', -1).skip(skip).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error retrieving from MongoDB: {e}")
        return []

# Get logs from MongoDB
def get_logs(limit=100, date=None):
    """Get logs from MongoDB"""
    db = get_db_connection()
    
    query = {}
    if date:
        # Query for logs on a specific date
        start_date = datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S")
        query = {
            "timestamp": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
        
    try:
        cursor = db[LOGS_COLLECTION].find(query).sort('timestamp', -1).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error retrieving logs from MongoDB: {e}")
        return [] 
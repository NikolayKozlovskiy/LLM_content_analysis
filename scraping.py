import pandas as pd
import uuid
from gnews import GNews
import concurrent.futures
from newspaper import Article
import nltk
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import os
import time  # Make sure to import the time module

# Download the NLTK 'punkt' resource
nltk.download('punkt')

# Initialize the GNews object with specified parameters
google_news = GNews(language='en', country='DE', start_date=(2018, 6, 1), end_date=(2024, 12, 31))

def fetch_news_for_keyword(keyword, max_results=20):
    articles = google_news.get_news(keyword)
    news_results = []
    count = 0
    for article in articles:
        if count < max_results:
            news_results.append({
                'Uuid': str(uuid.uuid4()),
                'Prompt': keyword,
                'Search engine': 'Google News',
                'URL': article['url'],
                'Type of document': 'news article',
                'Title': article['title'],
                'Published date': format_date(article['published date']),
                'Publisher': format_publisher(article.get('publisher', 'Unknown')),
                'Keywords': keyword
            })
            count += 1
        else:
            break
    return news_results

def fetch_news_for_keywords(keywords, max_results=20):
    return fetch_news_for_keyword(keywords, max_results)

def fetch_article_text(url, retries=3):
    for attempt in range(retries):
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            return {
                'Clean main text': sanitize_text(article.text),
                'Summary': sanitize_text(article.summary),
                'Download Status': 'Success'
            }
        except Exception as e:
            last_exception = e
            time.sleep(2)
    return {
        'Clean main text': '',
        'Summary': '',
        'Download Status': f'Failed: {str(last_exception)}'
    }

def sanitize_text(text):
    return re.sub(r'[^\x00-\x7F]+', ' ', text)

def format_publisher(publisher_info):
    if isinstance(publisher_info, dict):
        return publisher_info.get('title', 'Unknown')
    return publisher_info

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return date_obj.strftime('%b %Y')
    except ValueError:
        return date_str

def add_news_columns(df, keywords_column, max_results=20):
    df.ffill(inplace=True)
    for col in ['Risk category (short description)', 'country', 'sector']:
        if col not in df.columns:
            df[col] = ''

    all_news = df[keywords_column].apply(lambda x: fetch_news_for_keywords(x, max_results))
    news_flat = [item for sublist in all_news for item in sublist]
    news_df = pd.DataFrame(news_flat)

    print("Columns in news_df after flattening:", news_df.columns)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        article_texts = list(executor.map(fetch_article_text, news_df['URL']))

    text_df = pd.DataFrame(article_texts)
    news_df = pd.concat([news_df, text_df], axis=1)

    success_count = news_df[news_df['Download Status'] == 'Success'].shape[0]
    total_count = news_df.shape[0]
    print(f"Successfully downloaded {success_count} out of {total_count} articles.")

    news_df['Upload timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    news_df['Language of retrieval'] = 'en'

    expanded_df = pd.merge(df, news_df, left_on=keywords_column, right_on='Prompt', how='right')
    expanded_df['Download Status'] = news_df['Download Status']

    columns_order = [
        'Uuid', 'Risk category (short description)', 'country', 'Language of retrieval', 'sector',
        'Prompt', 'Search engine', 'URL', 'Type of document', 'Clean main text', 'Published date',
        'Publisher', 'Title', 'Keywords', 'Summary', 'Upload timestamp', 'Download Status'
    ]
    expanded_df = expanded_df[columns_order]

    return expanded_df

def truncate_value(value, max_length):
    if max_length is None or len(value) <= max_length:
        return value
    return value[:max_length]

def create_table_if_not_exists():
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST")
    )
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS news_data (
        Uuid UUID PRIMARY KEY,
        risk_category VARCHAR(1024),
        country VARCHAR(1024),
        language_of_retrieval VARCHAR(1024),
        sector VARCHAR(1024),
        prompt VARCHAR(1024),
        search_engine VARCHAR(1024),
        url VARCHAR(2048),
        type_of_document VARCHAR(1024),
        clean_main_text TEXT,
        published_date VARCHAR(1024),
        publisher VARCHAR(1024),
        title TEXT,
        keywords TEXT,
        summary TEXT,
        upload_timestamp TIMESTAMP,
        download_status VARCHAR(255)
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def save_to_postgresql(df):
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST")
    )
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO news_data (Uuid, risk_category, country, language_of_retrieval, sector, prompt, search_engine, url, type_of_document, clean_main_text, published_date, publisher, title, keywords, summary, upload_timestamp, download_status)
    VALUES %s
    ON CONFLICT (Uuid) DO NOTHING;
    """

    max_lengths = {
        'risk_category': 1024,
        'country': 1024,
        'language_of_retrieval': 1024,
        'sector': 1024,
        'prompt': 1024,
        'search_engine': 1024,
        'url': 2048,
        'type_of_document': 1024,
        'published_date': 1024,
        'publisher': 1024,
        'title': None,
        'clean_main_text': None,
        'keywords': None,
        'summary': None,
        'upload_timestamp': None,
        'download_status': 255
    }

    values = [
        (
            row['Uuid'], truncate_value(row.get('Risk category (short description)', ''), max_lengths['risk_category']), truncate_value(row.get('country', ''), max_lengths['country']),
            truncate_value(row.get('Language of retrieval', ''), max_lengths['language_of_retrieval']), truncate_value(row.get('sector', ''), max_lengths['sector']), truncate_value(row['Prompt'], max_lengths['prompt']),
            truncate_value(row['Search engine'], max_lengths['search_engine']), truncate_value(row['URL'], max_lengths['url']), truncate_value(row['Type of document'], max_lengths['type_of_document']),
            row.get('Clean main text', ''), truncate_value(row['Published date'], max_lengths['published_date']), truncate_value(row['Publisher'], max_lengths['publisher']),
            row['Title'], row['Keywords'], row.get('Summary', ''), row['Upload timestamp'],
            truncate_value(row['Download Status'], max_lengths['download_status'])
        )
        for index, row in df.iterrows()
    ]

    execute_values(cursor, insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description='Process an Excel file for keyword analysis.')
    parser.add_argument('file_path', type=str, help='Path to the Excel file')
    args = parser.parse_args()

    # List files in the /data directory for debugging
    print("Files in /data:")
    print(os.listdir('/data'))

    file_path = args.file_path

    # Example usage
    create_table_if_not_exists()

    keywords_df = pd.read_excel(file_path, sheet_name='04_Key word list')
    keywords_df.ffill(inplace=True)
    news_df = add_news_columns(keywords_df, 'Final list of key words', max_results=20)
    save_to_postgresql(news_df)
    print(news_df.head())


import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os

def fetch_data_from_db():
    conn_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(conn_string)
    query = "SELECT * FROM news_data;"
    df = pd.read_sql(query, engine)
    print(f"Data fetched from DB:\n{df.head()}")  # Debug print
    return df

def analyze_data(df):
    # Ensure the figures directory exists
    figures_dir = '/figures'
    os.makedirs(figures_dir, exist_ok=True)

    # Total Amount of Retrieved URLs per Prompt, per Risk Category, per Country
    total_urls = df.groupby(['prompt', 'risk_category', 'country']).size().reset_index(name='Total URLs')
    print(f"Total URLs:\n{total_urls.head()}")  # Debug print

    # Plot total URLs per prompt
    fig1 = px.bar(total_urls, x='Total URLs', y='prompt', color='country', title='Total Amount of Retrieved URLs per Prompt, per Risk Category, per Country')
    fig1.update_layout(yaxis_title='Prompt', xaxis_title='Total URLs')
    fig1.write_html(f"{figures_dir}/total_urls.html")

    # Bar Plot of Amount of URLs Distribution by Year
    df['Year'] = pd.to_datetime(df['published_date'], format='%b %Y', errors='coerce').dt.year
    urls_by_year = df.groupby('Year').size().reset_index(name='Total URLs')
    print(f"URLs by Year:\n{urls_by_year.head()}")  # Debug print

    # Plot URLs distribution by year
    fig2 = px.bar(urls_by_year, x='Year', y='Total URLs', title='Amount of URLs Distribution by Year')
    fig2.update_layout(yaxis_title='Total URLs', xaxis_title='Year')
    fig2.write_html(f"{figures_dir}/urls_by_year.html")

    # Download Status Analysis
    df['Download Status'] = df['download_status'].apply(lambda x: 'Success' if 'Success' in x else 'Failed')
    download_status = df.groupby(['prompt', 'Download Status']).size().reset_index(name='Count')
    print(f"Download Status:\n{download_status.head()}")  # Debug print

    # Plot download status per prompt
    fig3 = px.bar(download_status, x='Count', y='prompt', color='Download Status', title='Download Status per Prompt')
    fig3.update_layout(yaxis_title='Prompt', xaxis_title='Count')
    fig3.write_html(f"{figures_dir}/download_status.html")

def main():
    df = fetch_data_from_db()
    analyze_data(df)

if __name__ == "__main__":
    main()


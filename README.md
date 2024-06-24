# Automated Pipeline for News Scraping and Analysis

## Project Overview

This project is an automated pipeline designed for news scraping, natural language processing (NLP), and data analysis. It performs the following tasks:

1. Web Scraping: Retrieve article items and information from them.
2. NLP: Analyze the retrieved articles for social risk factors.
3. Reporting: Generate visual reports for the scraping and NLP results.
4. Data Management: Write the results to a remote database and local Excel files.

## Project Structure

```plaintext
my_project/
├── data/
│   └── 01_Social_listening_Nicaragua_Miriam_Done.xlsx
├── docker-compose.yml
├── Dockerfile
├── entrypoint.py
├── requirements.txt
├── data_analysis.py
├── figures/
└── scraping.py
```


## Setup

### Prerequisites

- Docker
- Docker Compose

### Initial Setup

1. **Clone the repository**:

    ```bash
    git clone https://github.com/NikolayKozlovskiy/dkv_auto_search.git
    cd dkv_auto_search
    ```

2. **Add your Excel file**:

    Place your Excel file in the `data` directory.

3. **Build and run the Docker containers**:

    ```bash
    docker-compose up --build
    ```

### Usage

#### Running the Scraping Script

To run the scraping script:

    ```bash
    docker-compose run app scraping /data/Your-excel-file.xlsx
    ```

#### Running the Data Analysis Script

To run the data analysis script:

    ```bash
    docker-compose run app data_analysis
    ```

## Output

### Figures

The generated HTML files will be saved in the `figures` directory.

- `figures/total_urls.html`
- `figures/urls_by_year.html`
- `figures/download_status.html`

### Environment Variables

The following environment variables are used in the `docker-compose.yml` file:

- `POSTGRES_DB`: The name of the PostgreSQL database.
- `POSTGRES_USER`: The PostgreSQL user.
- `POSTGRES_PASSWORD`: The password for the PostgreSQL user.
- `POSTGRES_HOST`: The hostname for the PostgreSQL database.
- `POSTGRES_PORT`: The port number for the PostgreSQL database.

Ensure these variables are correctly set in the `docker-compose.yml` file before running the containers.

## Troubleshooting

If you encounter any issues with the containers, try rebuilding them:

    ```bash
    docker-compose up --build
    ```

To stop the containers:

    ```bash
    docker-compose down
    ```

## License

This project is licensed under the MIT License.

## Acknowledgments

- GNews API
- Newspaper3k
- Plotly

import time
import logging
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from gnews import GNews
from newspaper import Article

from auto_internet_search.core.functions import delete_directory, check_or_create_dir, save_to_excel_country_risk_level
from auto_internet_search.core.constants.risk_categories import RiskCategories
from auto_internet_search.core.constants.key_words import KeyWords
from auto_internet_search.core.constants.columns import ColNames

class WebScraping:
    """A class to perform web scraping for news articles related to social risk categories."""

    DEFAULT_PROMPT_LANG = 'en'
    DEFAULT_DATA_SOURCE = 'google_news'
    DEFAULT_COMMODITY = "coffee"
    DEFAULT_RISK_CATEGORIES = ['child_labour']
    DEFAULT_COUNTRIES = ['Nicaragua']

    PROMPT_DICT = {
        'child_labour': [RiskCategories.child_labour, KeyWords.child_labour],
        'worst_form_child_labour': [RiskCategories.worst_form_child_labour, KeyWords.worst_form_child_labour],
        'forced_labour': [RiskCategories.forced_labour, KeyWords.forced_labour],
        'slavery': [RiskCategories.slavery, KeyWords.slavery],
        'work_related_health': [RiskCategories.work_related_health, KeyWords.work_related_health],
        'freedom_association': [RiskCategories.freedom_association, KeyWords.freedom_association],
        'no_discrimination': [RiskCategories.no_discrimination, KeyWords.no_discrimination],
        'withholding_wage': [RiskCategories.withholding_wage, KeyWords.withholding_wage],
        'soil_water_noise_emission': [RiskCategories.soil_water_noise_emission, KeyWords.soil_water_noise_emission],
        'unlawful_eviction': [RiskCategories.unlawful_eviction, KeyWords.unlawful_eviction],
        'hiring_private_forces': [RiskCategories.hiring_private_forces, KeyWords.hiring_private_forces],
        'chemicals_stockholm_convention': [RiskCategories.chemicals_stockholm_convention, KeyWords.chemicals_stockholm_convention]
    }

    SCHEMA = [
        ColNames.country,
        ColNames.risk_category_full_name,
        ColNames.commodity,
        ColNames.lang,
        ColNames.prompt,
        ColNames.data_source,
        ColNames.url,
        ColNames.title,
        ColNames.published_date,
        ColNames.publisher,
        ColNames.article_clean_text,
        ColNames.download_state,
        ColNames.manual_check_suggested,
        ColNames.reason_for_manual_check,
        ColNames.upload_time
    ]

    def __init__(self, component_config) -> None:
        """Initializes the WebScraping class with configuration parameters.

        Args:
            component_config (ConfigParser): Configuration parser object containing parameters.
        """
        self.config = component_config
        self.logger = logging.getLogger(__name__)
        
        self.risk_categories = self.config.geteval("risk_categories", fallback=self.DEFAULT_RISK_CATEGORIES)
        self.countries = self.config.geteval("countries", fallback=self.DEFAULT_COUNTRIES)
        self.start_date = self.config.geteval("start_date")
        self.end_date = self.config.geteval("end_date", fallback=datetime.now())
        self.max_results = self.config.getint("max_results", fallback=20)
        self.text_length_threshold = self.config.getint("text_length_threshold", fallback=50)
        self.max_workers = self.config.getint("max_workers", fallback=5)
        self.do_clear_output = self.config.getboolean("do_clear_output", fallback=False)
        self.output_dir = self.config.get("output_dir")

        if self.do_clear_output:
            delete_directory(self.output_dir)
        check_or_create_dir(self.output_dir)

    def retrieve_all_info(self, news_item: dict, prompt: str, country: str, risk_category: str, commodity: str, lang: str, data_source: str) -> list:
        """Retrieves all relevant information from a news item.

        Args:
            news_item (dict): A news item dictionary.
            prompt (str): The prompt used for fetching the news item.
            country (str): The country related to the news item.
            risk_category (str): The risk category related to the news item.
            commodity (str): The commodity related to the news item.
            lang (str): The language of the news item.
            data_source (str): The data source of the news item.

        Returns:
            list: A list of all retrieved information.
        """
        article_text, download_state = self.fetch_article_text(news_item['url'])
        manual_check_suggested, reason_for_manual_check = self.manual_check_applicability(download_state, article_text)

        result = [
            country,
            risk_category,
            commodity,
            lang,
            prompt,
            data_source,
            news_item['url'],
            news_item['title'],
            self.format_date(news_item['published date']),
            self.format_publisher(news_item.get('publisher', 'Unknown')),
            article_text,
            download_state,
            manual_check_suggested,
            reason_for_manual_check,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]

        return result

    def fetch_article_text(self, news_item_url: str, retries: int = 3) -> tuple:
        """Fetches and sanitizes the text of an article from its URL.

        Args:
            news_item_url (str): The URL of the news item.
            retries (int): Number of retries for fetching the article text.

        Returns:
            tuple: A tuple containing the download state and sanitized text.
        """
        for _ in range(retries):
            try:
                article = Article(news_item_url, http_success_only=False, fetch_images=False, language=self.DEFAULT_PROMPT_LANG)
                article.download()
                article.parse()
                return 'Success', self.sanitize_text(article.text)
            except Exception as e:
                last_exception = e
                time.sleep(2)
        return str(last_exception), None

    def manual_check_applicability(self, download_state: str, article_text: str) -> tuple:
        """Determines if a manual check is suggested and provides the reason.

        Args:
            download_state (str): The state of the article download.
            article_text (str): The text of the article.

        Returns:
            tuple: A tuple containing the manual check suggestion (bool) and the reason (str).
        """
        download_successful = download_state == 'Success'
        text_meets_length_requirement = len(article_text) >= self.text_length_threshold

        manual_check_suggested = True

        if not download_successful:
            reason_for_manual_check = 'download_failed'
        elif not text_meets_length_requirement:
            reason_for_manual_check = 'text_retrieved_is_too_small'
        else:
            manual_check_suggested = False
            reason_for_manual_check = None

        return manual_check_suggested, reason_for_manual_check

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitizes the text by removing non-ASCII characters.

        Args:
            text (str): The text to sanitize.

        Returns:
            str: The sanitized text.
        """
        return re.sub(r'[^\x00-\x7F]+', ' ', text)

    @staticmethod
    def format_publisher(publisher_info: dict) -> str:
        """Formats the publisher information.

        Args:
            publisher_info (dict): The publisher information.

        Returns:
            str: The formatted publisher information.
        """
        if isinstance(publisher_info, dict):
            return publisher_info.get('title', 'Unknown')
        return publisher_info

    @staticmethod
    def format_date(date_str: str) -> str:
        """Formats the date string to a standard format.

        Args:
            date_str (str): The date string.

        Returns:
            str: The formatted date string.
        """
        try:
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            return date_obj.strftime('%b %Y')
        except ValueError:
            return date_str

    def retrieve_web_scraping_info_per_country_risk(self, country_risk_articles: list, country_risk_prompts: list, country: str, risk_category: str) -> list:
        """Retrieves web scraping information for each country and risk category.

        Args:
            country_risk_articles (list): List of articles for the country and risk category.
            country_risk_prompts (list): List of prompts for the country and risk category.
            country (str): The country for which the information is retrieved.
            risk_category (str): The risk category for which the information is retrieved.

        Returns:
            list: A list of retrieved information.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_news_item = {
                executor.submit(self.retrieve_all_info, news_item, prompt, country, risk_category, self.DEFAULT_COMMODITY, self.DEFAULT_PROMPT_LANG, self.DEFAULT_DATA_SOURCE): news_item
                for news_item, prompt in zip(country_risk_articles, country_risk_prompts)
            }
            results = []
            for future in as_completed(future_to_news_item):
                try:
                    results.append(future.result())
                except Exception as exc:
                    self.logger.error(f'Generated an exception: {exc}')
            return results

    def run(self) -> None:
        """Executes the web scraping process."""
        google_news = GNews(language=self.DEFAULT_PROMPT_LANG, start_date=self.start_date, end_date=self.end_date, max_results=self.max_results)

        previous_country = None
        for country in self.countries:
            self.logger.info(f"Web Scraping for country: {country} started")
            for risk_category in self.risk_categories:
                if risk_category not in self.PROMPT_DICT:
                    self.logger.warning(f"Unknown risk category: {risk_category}")
                    continue

                self.logger.info(f"Starting risk category: {risk_category}")
                country_risk_articles = []
                country_risk_prompts = []

                for key_words in self.PROMPT_DICT[risk_category][1]:
                    prompt = f'{key_words} "{country}" "{self.DEFAULT_COMMODITY}"'
                    google_news_results = google_news.get_news(prompt)
                    self.logger.info(f"Stats per prompt: {prompt} -> {len(google_news_results)}")
                    country_risk_articles.extend(google_news_results)
                    country_risk_prompts.extend([prompt] * len(google_news_results))

                result_per_country_risk = self.retrieve_web_scraping_info_per_country_risk(country_risk_articles, country_risk_prompts, country, self.PROMPT_DICT[risk_category][0])

                mode = 'w' if country != previous_country else 'a'
                previous_country = country

                save_to_excel_country_risk_level(country, risk_category, result_per_country_risk, self.SCHEMA, self.output_dir, mode)
                self.logger.info(f"Results for {country}, {risk_category} are written to {self.output_dir} directory")

import time
import logging
import re
from datetime import datetime
from gnews import GNews
from newspaper import Article

from auto_internet_search.core.functions import delete_directory, check_or_create_dir, save_to_excel_country_risk_level
from auto_internet_search.core.constants.risk_categories import RiskCategories
from auto_internet_search.core.constants.key_words import KeyWords
from auto_internet_search.core.constants.columns import ColNames


class WebScraping:

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
        self.config = component_config
        self.logger = logging.getLogger(__name__)
        
        self.risk_categories = self.config.geteval("risk_categories", fallback=self.DEFAULT_RISK_CATEGORIES)
        self.countries = self.config.geteval("countries", fallback=self.DEFAULT_COUNTRIES)

        self.start_date = self.config.geteval("start_date")
        self.end_date = self.config.geteval("end_date", fallback=datetime.now())
        self.max_results = self.config.getint("max_results", fallback=20)
        self.text_length_threshold = self.config.getint("text_length_threshold", fallback=50)  # Add this line

        self.do_clear_output = self.config.getboolean("do_clear_output", fallback=False)
        self.output_dir = self.config.get("output_dir")

        if self.do_clear_output:
            delete_directory(self.output_dir)
        check_or_create_dir(self.output_dir)

    def retrieve_all_info(self, news_item, prompt, country, risk_category, commodity, lang, data_source):

        download_state, article_text = self.fetch_article_text(news_item['url'])
        manual_check_suggested, reason_for_manual_check = self.manual_check_aplicability(download_state, article_text)

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

    def fetch_article_text(self, news_item_url, retries=3):
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
    
    def manual_check_aplicability(self, download_state, article_text): 

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
    def sanitize_text(text):
        return re.sub(r'[^\x00-\x7F]+', ' ', text)

    @staticmethod
    def format_publisher(publisher_info):
        if isinstance(publisher_info, dict):
            return publisher_info.get('title', 'Unknown')
        return publisher_info

    @staticmethod
    def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            return date_obj.strftime('%b %Y')
        except ValueError:
            return date_str

    def retrieve_web_scraping_info_per_country_risk(self, country_risk_articles, country_risk_prompts, country, risk_category):
        return [
            self.retrieve_all_info(news_item, prompt, country, risk_category, self.DEFAULT_COMMODITY, self.DEFAULT_PROMPT_LANG, self.DEFAULT_DATA_SOURCE)
            for news_item, prompt in zip(country_risk_articles, country_risk_prompts)
        ]

    def run(self) -> None:
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
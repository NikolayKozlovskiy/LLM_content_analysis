from datetime import datetime
from gnews import GNews

from auto_internet_search.core.constants.risk_categories import RiskCategories
from auto_internet_search.core.constants.key_words import KeyWords

class WebScraping():

    default_risk_categories = ['child_labour', 'worst_form_child_labour']
    default_countries = ['Nicaragua']

    default_prompt_lang = 'en'

    prompt_dict = {
        'child_labour' : [RiskCategories.child_labour, KeyWords.child_labour], 
        'worst_form_child_labour' : [RiskCategories.worst_form_child_labour, KeyWords.worst_form_child_labour]
    }

    def __init__(self, component_config) -> None:
        self.config = component_config

        self.risk_categories = self.config.geteval("risk_categories", fallback=self.default_risk_categories)
        self.countries = self.config.geteval("countries", fallback=self.default_countries)

        self.start_date = self.config.geteval("start_date")
        self.end_date = self.config.geteval("end_date", fallback=datetime.now())
        self.max_results = self.config.getint("max_results", fallback=20)

    def run(self)-> None: 
        google_news = GNews(language=self.default_prompt_lang, start_date=self.start_date, end_date=self.end_date, max_results=self.max_results)

        for country in self.countries:
            for risk_category in self.risk_categories:
                if risk_category in self.prompt_dict.keys():
                    for key_words in self.prompt_dict[risk_category][1]:

                        prompt = f'{key_words} "{country}" "coffee"'
                        articles = google_news.get_news(prompt)
                        print(len(articles))
                else:
                    continue
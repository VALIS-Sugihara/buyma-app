from abc import ABCMeta, abstractmethod

import requests
from bs4 import BeautifulSoup
import pandas as pd

class Meta(metaclass=ABCMeta):
    @abstractmethod
    def search(self):
        """[summary]
        """        
        pass

    @abstractmethod
    def make_url(self):
        pass

    @abstractmethod
    def get_html(self):
        pass

    @abstractmethod
    def get_data(self, properties):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def scoop(self):
        pass


class Lyst():
    TOP_URL = "https://www.lyst.com/"
    # SEARCH_URL = "https://www.lyst.com/search/?q=margiela+pants"
    SEARCH_URL = "https://www.lyst.com/search/"
    search_properties = {
        "QUERY_PARAM": "q",
        "AND_METHOD": "+"
    }
    collect_properties = {
        "METHOD": "select",
        # ""
    }
    structure = {
        ".product-feed__segment-items > .product-card   ": {
            ".product-card__designer": "brand",
            ".product-card__short-description-name": "title",
            ".product-card__details a": "href",
            "del.product-card__price": "origin_price",
            "span.product-card__price": "price",
            "span.product-card__discount-info": "discount_rate"
        }
    }

    def activate_search(self, keywords:list=[]):
        self.search_properties["AND_METHOD"].join(keywords)

    def collect(self, target):
        pass


class Client():
    url = None
    soup = None

    def __init__(self, activator: object = None, driver=requests):
        self._driver = driver
        self._activator = activator

    def scoop(self):
        response = self._driver.get(self.url)
        if self._driver is requests:
            self.soup = BeautifulSoup(response.text, 'html.parser')
        else:
            self.soup = BeautifulSoup(self._driver.page_source, 'html.parser')


    def search(self, keywords:list=[]):
        self.url = self._activator.activate_search(keywords)
        self.scoop()

    def collect(self):
        self.url = self._activator.activate_collect()
        self.scoop()


class Activator():

    def __init__(self, channel: object=None):
        self._channel = channel

    def activate_search(self, keywords:list=[]):
        query = "?{}={}".format(self._channel.search_properties["QUERY_PARAM"], self._channel.search_properties["AND_METHOD"].join(keywords))
        return self._channel.SEARCH_URL + query

    def activate_collect(self, keywords:list=[]):
        self._channel.search_properties["AND_METHOD"].join(keywords)

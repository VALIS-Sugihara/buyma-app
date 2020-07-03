from abc import ABCMeta, abstractmethod

TOP_URL = "https://www.buyma.com"
SHOP_URL = "https://www.buyma.com/buyer/%s.html"
POST_URL = "https://www.buyma.com/buyer/%s/post/index.html"
RANK_URL = "https://www.buyma.com/buyer/%s/rank_%s.html"
ITEM_URL = "https://www.buyma.com/buyer/%s/item_%s.html"
SALES_URL = "https://www.buyma.com/buyer/%s/sales_%s.html"


class Buyma(metaclass=ABCMeta):
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
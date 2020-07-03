import re
import requests
from bs4 import BeautifulSoup

TOP_URL = "https://www.buyma.com"
SHOP_URL = "https://www.buyma.com/buyer/%s.html"
POST_URL = "https://www.buyma.com/buyer/%s/post/index.html"
RANK_URL = "https://www.buyma.com/buyer/%s/rank_%s.html"
ITEM_URL = "https://www.buyma.com/buyer/%s/item_%s.html"
SALES_URL = "https://www.buyma.com/buyer/%s/sales_%s.html"


class Shop():
    title = "ホーム"
    categories = (
        "Post",  # 記事
        "Rank",  # 評価
        "Item",  # 最新商品
        "Sales",  # 注文実績
    )

    def __init__(self, tpl: tuple, categories=()):
        self.name = str(tpl[0])
        self.id = str(tpl[1])
        self.url = self.make_url()
        # self.shop_url = self._get_shop_url()
        self._soup = self.get_html()
        # self.sales_url = TOP_URL + self._get_sales_url()
        # self.sales_total_pages = self._get_sales_total_pages()
        for category in categories:
            if category == "Post":
                self.post = Post(self)
            if category == "Rank":
                self.rank = Rank(self)
            if category == "Item":
                self.item = Item(self)
            if category == "Sales":
                self.sales = Sales(self)
        self.is_valid()        

    def make_url(self):
        return SHOP_URL % (self.id)

    def get_html(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def get_data(self, properties):
        pass

    def is_valid(self):
        if self.name is None:
            raise AttributeError
        if self.id is None:
            raise AttributeError
        if self.url != SHOP_URL % (self.id,):
            raise AttributeError
        print("====== This Shop is  =====")
        print("Name is ...", self.name)
        print("Id is ...", self.id)
        print("Shop.url is ...", self.url)
        print("====== ===== =====")


class Sales():
    title = "注文実績"
    categories = ()

    def __init__(self, Shop):
        self.__shop = Shop
        self.url = self.make_url()
        self._soup = self.get_html()
        self.total_page = self.get_total_page()
        self.is_valid()        

    def make_url(self):
        soup = self.__shop._soup
        elms = soup.select_one('a:contains("注文実績")')
        href = elms["href"]
        return TOP_URL + href

    def get_html(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def get_total_page(self):
        elms = self._soup.select_one('.pager a:contains("最後")')
        href = elms["href"]

        ptn = r"^.+sales_(\d+).html$"
        total_page = re.sub(ptn, r"\1", href)
        return int(total_page)

    def is_valid(self):
        # if self.name is None:
        #     raise AttributeError
        # if self.id is None:
        #     raise AttributeError
        if self.url != SALES_URL % (self.__shop.id, "1",):
            raise AttributeError
        if not isinstance(self.total_page, int):
            raise AttributeError
        print("====== This Shop.Sales is  =====")
        print("Name is ...", self.__shop.name)
        print("Id is ...", self.__shop.id)
        print("Sales.url is ...", self.url)
        print("Sales.total_page is ...", self.total_page)
        print("====== ===== =====")


class Post():
    pass


class Rank():
    pass


class Item():
    pass

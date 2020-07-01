import re
import requests
from bs4 import BeautifulSoup

TOP_URL = "https://www.buyma.com"
SHOP_URL = "https://www.buyma.com/buyer/%s.html"
SALES_URL = "https://www.buyma.com/buyer/%s/sales_%s.html"


class Shop():

    def __init__(self, tpl):
        self.name = tpl[0]
        self.id = tpl[1]
        self.shop_url = self._get_shop_url()
        self.sales_url = TOP_URL + self._get_sales_url()
        self.sales_total_pages = self._get_sales_total_pages()
        self.is_valid()

    def _get_shop_url(self):
        return SHOP_URL % (self.id)

    def _get_sales_url(self):
        # TODO:: ErrorHandling
        response = requests.get(self.shop_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elms = soup.select_one('a:contains("注文実績")')
        href = elms["href"]
        return href
        
    def _get_sales_total_pages(self):
        response = requests.get(self.sales_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elms = soup.select_one('.pager a:contains("最後")')
        href = elms["href"]

        ptn = r"^.+sales_(\d+).html$"
        total_page = re.sub(ptn, r"\1", href)
        return int(total_page)

    def is_valid(self):
        if self.name is None:
            raise AttributeError
        if self.id is None:
            raise AttributeError
        if self.shop_url != SHOP_URL % (self.id,):
            raise AttributeError
        if self.sales_url != SALES_URL % (self.id, "1",):
            raise AttributeError
        if isinstance(self.sales_total_pages, int) is not True:
            raise AttributeError
        print("====== This Shop is  =====")
        print("Name is ...", self.name)
        print("Id is ...", self.id)
        print("ShopUrl is ...", self.shop_url)
        print("SalesUrl is ...", self.sales_url)
        print("SalesTotalPages is ...", self.sales_total_pages)
        print("====== ===== =====")

    def get_sales_now_url(self, page: int):
        return SALES_URL % (self.id, str(page),)

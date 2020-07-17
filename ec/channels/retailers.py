import time
from .._driver import Chrome, Requests


class Retailer():
    def __init__(self):
        pass

    def search(self, url: str = ""):
        """ 汎用 search メソッド 
        指定したURLをリクエストし、
        HTMLソースを自身へセットする.
        """
        # _term 毎に振る舞いを変える

        # 個別のアクションを追記
        self.driver.access(url)
        # HTML を取得
        self.html = self.driver.get_html(url)

    def activate_search(self, keywords: list = []):
        """ search 前に URL を作成し、返却する """
        return self.url

    def collect(self, client, **add_property):
        units = client.soup.select(self.get_structure("units"))
        # 追加プロパティ設定（カラム）
        _columns = []
        if any(add_property):
            _columns = [k for k in add_property.keys()]
        columns = _columns + [k for k in self.get_structure("targets").keys()]

        data, i = {}, 0
        for unit in units:
            # 追加プロパティ設定（値）
            _data = []
            if any(add_property):
                _data = [v for v in add_property.values()]
            for target, selector in self.get_structure("targets").items():
                # print(target, selector)
                if selector is False:
                    _data.append("")
                else:
                    if target == "href":
                        _data.append(unit.select_one(selector)["href"] if unit.select_one(selector) is not None else None)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns

    def get_structure(self, type_: str = "units"):
        return self.structure[self._term][type_]


class Ruelala(Retailer):
    name = "ruelala.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.ruelala.com/boutique/"
    structure = [
        {
            "units": "#product_detail_page",
            "targets": {
                "retailer_brand": "#product_header > h1 > a",
                "retailer_title": "#product_header h1",
                "retailer_price": "span.list-price span.value.bfx-price",
                "retailer_origin_price": "span.msrp span.value.bfx-price",
                "retailer_sku": False
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Chrome()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url


class Mytheresa(Retailer):
    name = "mytheresa.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.mytheresa.com/en-jp/"
    structure = [
        {
            "units": "div.product-view",
            "targets": {
                "retailer_brand": ".catalog-product-view .product-shop .product-designer",
                "retailer_title": ".catalog-product-view .product-name span",
                "retailer_price": ".catalog-product-view .product-shop .special-price span.price",
                "retailer_origin_price": ".catalog-product-view .product-shop .old-price span.price",
                "retailer_sku": ".product-sku span.h1"
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Farfetch(Retailer):
    name = "farfetch.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.farfetch.com/"
    structure = [
        {
            "units": "div._6c4acd",
            "targets": {
                "retailer_brand": "._e87472._346238._e4b5ec",
                "retailer_title": "._d85b45._d85b45._1851d6",
                "retailer_price": "._e806a1._366381._d85b45",
                "retailer_origin_price": "._89a1d3._b764f1",
                "retailer_sku": "._9d3f24._da3196 ._4919a3._da3196 ._84497d._e7b42f ._d85b45"
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Vitkac(Retailer):
    name = "vitkac.com"
    keyword = ""
    html = None
    TOP_URL = "hhttps://www.vitkac.com/"
    structure = [
        {
            "units": "section.Fproducts",
            "targets": {
                "retailer_brand": ".prod-header-module h1 a",
                "retailer_title": "span#w_header",
                "retailer_price": "span#regularPrice",
                "retailer_origin_price": "p#salePrice",
                "retailer_sku": "span#productSymbol"
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Modes(Retailer):
    name = "modes.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.modes.com/"
    structure = [
        {
            "units": "main._3n7Wt",
            "targets": {
                "retailer_brand": "a.P9bAO",
                "retailer_title": "._1CC2G._3XCDb",
                "retailer_price": "span._677BI",
                "retailer_origin_price": "span._1WTWk",
                "retailer_sku": "._2T8be._2farf"
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Forzieri(Retailer):
    name = "forzieri.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.eu.forzieri.com/"
    structure = [
        {
            "units": "#productDetails",
            "targets": {
                "retailer_brand": "span.brand-name a",
                "retailer_title": "span.product-name",
                "retailer_price": "span#salePrice",
                "retailer_origin_price": "span#listPrice",
                "retailer_sku": "span#productSku"
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Mybag(Retailer):
    name = "mybag.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.mybag.com/"
    structure = [
        {
            "units": "div.athenaProductPage_topRow",
            "targets": {
                "retailer_brand": "div[data-information-component='brand'] div",
                "retailer_title": "h1.productName_title",
                "retailer_price": "p.productPrice_price",
                "retailer_origin_price": "p.productPrice_rrp",
                "retailer_sku": False,
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url


class Coggles(Retailer):
    name = "coggles.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.coggles.com/"
    structure = [
        {
            "units": "div.athenaProductPage_topRow",
            "targets": {
                "retailer_brand": ".productBrandLogoText",
                "retailer_title": "h1.productName_title",
                "retailer_price": "p.productPrice_price",
                "retailer_origin_price": "p.productPrice_rrp",
                "retailer_sku": False,
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url

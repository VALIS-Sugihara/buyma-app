import time
from .._driver import Chrome, Requests


class Malls():
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
                print(target, selector)
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


class BuymaItems(Malls):
    name = "buyma.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.buyma.com/"
    SEARCH_URL = "https://www.buyma.com/r/-F1/%s/"
    search_properties = {
        "AND_METHOD": "%20"
    }
    structure = [
        {
            "units": "li.product",
            "targets": {
                "malls_price": ".product_price_detail .Price_Txt",
            }
        }
    ]
    driver = Requests()
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url=""):
        self.url = url

    def activate_search(self, keywords: list = []):
        return self.SEARCH_URL % (self.search_properties["AND_METHOD"].join(keywords),)

    @classmethod
    def compare(cls, target_price: float, prices: [int]):
        active = 1
        for price in prices:
            # TODO:: filtered
            if float(target_price) * 1.2 > float(price.replace("¥", "").replace(",", "").strip()):
                active = 0
        return active
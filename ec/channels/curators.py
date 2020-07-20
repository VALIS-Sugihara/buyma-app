import time
from .._driver import Chrome, Requests


class Curator():
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
        self.html = self.driver.get_html()

    def activate_search(self, keywords: list = []):
        """ search 前に URL を作成し、返却する """
        query = "?{}={}".format(self.search_properties["QUERY_PARAM"], self.search_properties["AND_METHOD"].join(keywords))
        return self.SEARCH_URL % (query,)

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


class Lyst(Curator):
    name = "Lyst.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.lyst.com/"
    SEARCH_URL = "https://www.lyst.com/search/%s"
    search_properties = {
        "QUERY_PARAM": "q",
        "AND_METHOD": "+"
    }
    structure = [
        {
            "units": ".product-feed__segment-items > .product-card   ",
            "targets": {
                "brand": ".product-card__designer",
                "title": ".product-card__short-description-name",
                "href": ".product-card__image-wrapper a",
                "origin_price": "del.product-card__price",
                "price": "span.product-card__price",
                "discount_rate": "span.product-card__discount-info",
                "retailer": ".product-card__affiliate__retailer span"
            }
        },
        {
            "units": "body",
            "targets": {
                "href": "a:contains('click here')"
            }
        },
    ]
    driver = Chrome()
    more_button = "_3ULMm"
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = len(structure)

    def __init__(self):
        super().__init__()

    def search(self, url: str = ""):
        # _term 毎に振る舞いを変える
        
        # 個別のアクションを追記
        self.driver.access(url)

        # timeout 変更
        self.driver._driver.set_page_load_timeout(300)
        self.driver._driver.implicitly_wait(300)
        for i in range(0, 50):
        # for i in range(0, 2):  # TEST
            self.driver._driver.find_element_by_class_name(self.more_button).click()
            time.sleep(5)
        # HTML を取得
        self.html = self.driver.get_html()

    def collect(self, client, **add_property):
        # １階層目
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
                        # ２階層目
                        _href = unit.select_one(selector)["href"] if unit.select_one(selector) is not None else None
                        if _href is not None:
                            # super().search(_href)
                            req = Requests()
                            self.html = req.get_html(_href)
                            client.scoop()
                            # _term を変更
                            self._term = 1
                            d, c = super().collect(client)
                            # _term を戻す
                            self._term = 0
                            _href = d[0][0]
                        _data.append(self.TOP_URL + _href)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1

        return data, columns

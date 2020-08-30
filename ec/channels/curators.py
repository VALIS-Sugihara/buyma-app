import time
from .._driver import Chrome, Requests


# memo
# https://www.ikrix.com/jp/home-men


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
        self.driver.wait()
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
        "DISCOUNT_RATE": "discount_from",
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
    more_button = "_3ULMm"
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = len(structure)

    def __init__(self):
        super().__init__()
        self.driver = Chrome()

    def activate_search(self, keywords: list = [], discount_rate=50):
        """ search 前に URL を作成し、返却する """
        query = "?{}={}".format(self.search_properties["QUERY_PARAM"], self.search_properties["AND_METHOD"].join(keywords))
        if str(discount_rate) in ("1", "20", "50", "70"):
            query += "&" + self.search_properties["DISCOUNT_RATE"] + "=" + str(discount_rate)
        return self.SEARCH_URL % (query,)

    def search(self, url: str = ""):
        # _term 毎に振る舞いを変える
        
        # 個別のアクションを追記
        self.driver.access(url)
        self.driver.wait()

        # timeout 変更
        self.driver._driver.set_page_load_timeout(500)
        self.driver._driver.implicitly_wait(500)
        try:
            for i in range(0, 50):
            # for i in range(0, 2):  # TEST
                self.driver._driver.find_element_by_class_name(self.more_button).click()
                time.sleep(5)
        except Exception as e:
            print("Exception Occured ...", e.args[0])
        finally:
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
                if selector is False:
                    _data.append("")
                else:
                    if target == "href":
                        # ２階層目
                        _href = unit.select_one(selector)["href"] if unit.select_one(selector) is not None else None
                        if _href is not None:
                            # super().search(_href)
                            req = Requests()
                            req.access(_href)
                            self.html = req.get_html()
                            client.scoop()
                            # _term を変更
                            self._term = 1
                            d, c = super().collect(client)
                            print(d)
                            # _term を戻す
                            self._term = 0
                            try:
                                _href = d[0][0]
                                _href = self.TOP_URL + _href
                            except Exception as e:
                                print("Eception Occured ...", e.args[0])
                                _href = None
                        _data.append(_href)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1

        return data, columns


class Shoppingscanner(Curator):
    name = "Shoppingscanner.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.shoppingscanner.com/"
    SEARCH_URL = "https://www.shoppingscanner.com/search/index/condition-new/sale-%s-100/%s&sort=ranking&order=ASC"
    search_properties = {
        "QUERY_PARAM": "k",
        "AND_METHOD": "%20"
    }
    structure = [
        {
            "units": "#article > div > section > div.shop-items-wrap > div.lcd-shop-item.product",
            "targets": {
                "brand": "div.lcd-item-info > a:nth-child(1) > h6",
                "title": "div.lcd-item-info > a:nth-child(2) > h6",
                "href": "div.lcd-shop-item-wrap > a",
                # "origin_price": False,
                "price": "div.lcd-item-info > span.lcd.lcd-price-container > h6",
                # "discount_rate": False,
                "retailer": "div.shop-info.no-highlight"
            }
        },
        {
            "units": "#main",
            "targets": {
                "href": "a:contains('click here')"
            }
        },
    ]
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 1

    def __init__(self):
        super().__init__()
        self.driver = Chrome()

    def activate_search(self, keywords: list = [], discount_rate=30):
        """ search 前に URL を作成し、返却する """
        query = "?{}={}".format(self.search_properties["QUERY_PARAM"], self.search_properties["AND_METHOD"].join(keywords))
        if str(discount_rate) not in ("0", "20", "30", "50"):
            discount_rate = 50
        return self.SEARCH_URL % (str(discount_rate), query,)

    def search(self, url: str = ""):
        # _term 毎に振る舞いを変える
        
        # 個別のアクションを追記
        self.driver.access(url)
        self.driver.wait()

        # timeout 変更
        self.driver._driver.set_page_load_timeout(500)
        self.driver._driver.implicitly_wait(500)
        try:
            for i in range(0, 50):
            # for i in range(0, 1):
                self.driver._driver.execute_script("document.getElementById('page-footer').scrollIntoView(true)")
                time.sleep(5)
        except Exception as e:
            print("Exception Occured ...", e.args[0])
        finally:
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
            try:
                # 追加プロパティ設定（値）
                _data = []
                if any(add_property):
                    _data = [v for v in add_property.values()]
                for target, selector in self.get_structure("targets").items():
                    if selector is False:
                        _data.append("")
                    else:
                        if target == "href":
                            # ２階層目
                            _href = unit.select_one(selector)["href"] if unit.select_one(selector) is not None else None
                            if _href is not None:
                                # super().search(_href)
                                req = Requests()
                                req.access(_href)
                                self.html = req.get_html()
                                client.scoop()
                                # _term を変更
                                self._term = 1
                                d, c = super().collect(client)
                                # _term を戻す
                                self._term = 0
                                _href = d[0][0]
                            _data.append(_href)
                        else:
                            _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
                data[i] = _data
                i += 1
                # print(_data)
            except Exception as e:
                print("Exception is Occured", e.args[0])
                data[i] = [None for c in columns]
                i += 1
                continue

        return data, columns


class Articture(Curator):
    name = "articture.com"
    keyword = ""
    html = None
    TOP_URL = "https://articture.com"
    SEARCH_URL = "https://articture.com/search%s"
    search_properties = {
        "QUERY_PARAM": "q",
        "AND_METHOD": "&"
    }
    structure = [
        {
            "units": ".ProductItem ",
            "targets": {
                "brand": "",
                "title": ".ProductItem__Title > a",
                "href": ".ProductItem__Title > a",
                # "origin_price": False,
                "price": ".ProductItem__Price",
                # "discount_rate": False,
                "retailer": ""
            }
        }
    ]
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0
    next_btn = 'a[title="Next page"]'
    next_page = True

    def __init__(self):
        super().__init__()
        self.driver = Requests()
        self.cnt = 0  # アイテム数カウント用

    def activate_search(self, keywords: list = []):
        if self.next_page is True:
            """ search 前に URL を作成し、返却する """
            query = "?{}={}".format(self.search_properties["QUERY_PARAM"], self.search_properties["AND_METHOD"].join(keywords))
            return self.SEARCH_URL % (query,)
        else:
            """ next_page があった場合はそれを返す """
            return self.next_page

    def collect(self, client, **add_property):
        units = client.soup.select(self.get_structure("units"))
        # 追加プロパティ設定（カラム）
        _columns = []
        if any(add_property):
            _columns = [k for k in add_property.keys()]
        columns = _columns + [k for k in self.get_structure("targets").keys()]

        data = {}
        for unit in units:
            try:
                # 追加プロパティ設定（値）
                _data = []
                if any(add_property):
                    _data = [v for v in add_property.values()]
                for target, selector in self.get_structure("targets").items():
                    if selector is False:
                        _data.append("")
                    else:
                        if target == "href":
                            _href = self.TOP_URL + unit.select_one(selector)["href"] if unit.select_one(selector) is not None else None
                            _data.append(_href)
                        elif target == "brand" or target == "retailer":
                            _data.append("Articture")
                        else:
                            _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
                data[self.cnt] = _data
                self.cnt += 1
                # 次ページを更新
                self.next_page = self.TOP_URL + client.soup.select_one(self.next_btn)["href"]
                # print(_data)
            except Exception as e:
                print("Exception is Occured", e.args[0])
                data[self.cnt] = [None for c in columns]
                self.cnt += 1
                self.next_page = None
                continue

        return data, columns

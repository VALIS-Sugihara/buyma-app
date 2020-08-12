import time
import re
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
        self.driver.wait()
        # HTML を取得
        self.html = self.driver.get_html()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector) if any(unit.select(selector)) else []
                        img_urls = "@@@".join([img_url["src"] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
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
                "retailer_description": "#product_details_details",
                "retailer_price": "span.list-price span.value.bfx-price",
                "retailer_origin_price": "span.msrp span.value.bfx-price",
                "retailer_sku": "#product_header h1",
                "retailer_images": ('//*[@id="thumbnail_images"]/a', "background",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

    def search(self, url: str = ""):
        """ search メソッド 
        指定したURLをリクエストし、
        HTMLソースを自身へセットする.
        """
        # 個別のアクションを追記
        self.driver.access(url)
        # 画像がcssのためプロパティを別途取得
        try:
            selector = self.get_structure("targets")["retailer_images"]
            images = self.driver._driver.find_elements_by_xpath(selector[0])
            img_urls = [img.value_of_css_property(selector[1]) for img in images]
            # //asset1.ruecdn.com/images/product/111120/1111209342_RLLA_1.jpg を https://asset1.ruecdn.com/images/product/111120/1111209342_RLLD_1.jpg へ変換
            ptn = r"^.*url\(\"(.+)\"\).*$"
            img_urls = [re.sub(ptn, r"\1", img_url).replace("_RLLA_", "_RLLD_") for img_url in img_urls]
            self.img_urls = "@@@".join(img_urls)
        except Exception as e:
            print("Exception Occured ... ", e.args[0])
            self.img_urls = None

        # HTML を取得
        self.html = self.driver.get_html()

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
                    if target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_images":
                        _data.append(self.img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Mytheresa(Retailer):
    name = "mytheresa.com"
    keyword = ""
    html = None
    TOP_URL = "×"
    structure = [
        {
            "units": "div.product-view",
            "targets": {
                "retailer_brand": ".catalog-product-view .product-shop .product-designer",
                "retailer_title": ".catalog-product-view .product-name span",
                "retailer_description": "div.product-shop > div.product-collateral.toggle-content.accordion-open > dl",
                "retailer_price": ".price-info .price-box .regular-price .price",
                "retailer_origin_price": ".catalog-product-view .product-shop .old-price span.price",
                "retailer_sku": ".product-sku span.h1",
                "retailer_images": ".slick-slide > img.gallery-image",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Chrome()


class Farfetch(Retailer):
    name = "farfetch.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.farfetch.com/"
    structure = [
        {
            "units": "#slice-pdp > div > div._6c4acd",
            "targets": {
                "retailer_brand": "._e87472._346238._e4b5ec",
                "retailer_title": "._d85b45._d85b45._1851d6",
                "retailer_description": "[data-tstid='productDetails']",
                "retailer_price": "[data-tstid='priceInfo-onsale']",
                "retailer_origin_price": "[data-tstid='priceInfo-original']",
                "retailer_sku": "._9d3f24._da3196 ._4919a3._da3196 ._84497d._e7b42f ._d85b45",
                "retailer_images": "[itemprop='image']",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Requests()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector) if any(unit.select(selector)) else []
                        img_urls = "@@@".join([img_url["content"] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Vitkac(Retailer):
    name = "vitkac.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.vitkac.com/"
    structure = [
        {
            "units": "section.Fproducts",
            "targets": {
                "retailer_brand": ".prod-header-module h1 a",
                "retailer_title": "span#w_header",
                "retailer_description": ".productDescription",
                "retailer_price": "span#regularPrice",
                "retailer_origin_price": "p#salePrice",
                "retailer_sku": "span#productSymbol",
                "retailer_images": "#slideShow > div.miniSlider > div > span.mini img",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Requests()


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
                "retailer_description": "#description-info-content > div > div",
                "retailer_price": "span._677BI",
                "retailer_origin_price": "span._1WTWk",
                "retailer_sku": "._2T8be._2farf",
                "retailer_images": "div._37T5Z._2PdLC > div._10LDn > div._1Nbfy img",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Chrome()


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
                "retailer_description": "#descriptionProduct > div > p:nth-child(1)",
                "retailer_price": "span#salePrice",
                "retailer_origin_price": "span#listPrice",
                "retailer_sku": "span#productSku",
                "retailer_images": "#productGallery > div.sticky-wrap.gallery-wrap > div.product-image-wrap img",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Requests()


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
                "retailer_description": "#product-description-content-lg-2 > div > div",
                "retailer_price": "p.productPrice_price",
                "retailer_origin_price": "p.productPrice_rrp",
                "retailer_sku": "h1.productName_title",
                "retailer_images": "div.athenaProductPage_imageContainer div.athenaProductImageCarousel_imagesContainer img.athenaProductImageCarousel_image",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Requests()


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
                "retailer_description": "#product-description-content-lg-2 > div",
                "retailer_price": "p.productPrice_price",
                "retailer_origin_price": "p.productPrice_rrp",
                "retailer_sku": "h1.productName_title",
                "retailer_images": "img.athenaProductImageCarousel_image",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url):
        self.url = url
        self.driver = Requests()


class Cettire(Retailer):
    name = "cettire.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.cettire.com/"
    structure = [
        {
            "units": "#MainContent > div > div > div",
            "targets": {
                "retailer_brand": "div.grid__item.medium-up--two-fifths > div > div.product-single__meta.small--hide.small--text-center > p > a",
                "retailer_title": "div.grid__item.medium-up--two-fifths > div > div.product-single__meta.small--hide.small--text-center > h1",
                "retailer_description": "div.grid__item.medium-up--two-fifths > div > div.rte.product-single__description",
                "retailer_price": "span#ProductPrice",
                "retailer_origin_price": "#ComparePrice",
                "retailer_sku": "div.grid__item.medium-up--two-fifths > div > div.product-single__meta.small--hide.small--text-center > h1",
                "retailer_images": ".product-single__thumbnail-item a img",
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        ptn = r"^.*Designer Model Number: (.+)Designer Colour:.*$"
                        _selector = self.structure[0]["targets"]["retailer_description"]
                        desc = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else None
                        sku = re.sub(ptn, r'\1', desc) if desc is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector) if any(unit.select(selector)) else []
                        img_urls = "@@@".join([img_url["src"] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Ssense(Retailer):
    name = "ssense.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.ssense.com"
    structure = [
        {
            "units": "#product-item > div.product-item-container.row-fluid",
            "targets": {
                "retailer_brand": "div.span3.offset1.product-item-description.tablet-landscape-full-fluid-width > div > div > div > div > div > div > div.content > h1.product-brand > a",
                "retailer_title": "div.span3.offset1.product-item-description.tablet-landscape-full-fluid-width > div > div > div > div > div > div > div.content > h2",
                "retailer_description": "div.span3.offset1.product-item-description.tablet-landscape-full-fluid-width > div > div > div > div > div > div > div.content > div > p > span:nth-child(1)",
                "retailer_price": "div.span3.product-cta-container > div > div > div > div > div > div > div.row-fluid > div.span16.price-container > h3 > span",
                "retailer_origin_price": "div.span3.product-cta-container > div > div > div > div > div > div > div.row-fluid > div.span16.price-container > h3 > span",
                "retailer_sku": "div.span3.offset1.product-item-description.tablet-landscape-full-fluid-width > div > div > div > div > div > div > div.content > span",
                "retailer_images": ("div.span8.product-item-images.smartphone-portrait-narrow-full-fluid-width .product-images-container .image-wrapper picture > img", "data-srcset",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Luisaviaroma(Retailer):
    name = "luisaviaroma.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.luisaviaroma.com"
    structure = [
        {
            "units": "#root-body > div > div > div.item__imageContainer___2CdjxFiLp1.flexboxgrid2__row___3a-jZNt8IN",
            "targets": {
                "retailer_brand": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div:nth-child(1) > h1 > a",
                "retailer_title": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div:nth-child(1) > div:nth-child(2) > div > p",
                "retailer_description": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div.item__marginTop20___1ddlyldUQW.flexboxgrid2__row___3a-jZNt8IN > div > div > div:nth-child(1) > div.ListContainer__ListContainerCls___24n4GSb7AI > div > ul",
                "retailer_price": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > strong > div > span",
                "retailer_origin_price": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > strong > div > span",
                "retailer_sku": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div.item__marginTop20___1ddlyldUQW.flexboxgrid2__row___3a-jZNt8IN > div > div > div:nth-child(1) > div.ListContainer__ListContainerCls___24n4GSb7AI > div > ul > li:nth-child(1)",
                "retailer_images": (".slick-slide > div > div > img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        ptn = r"^.*Item Code:(.+)$"
                        desc = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        sku = re.sub(ptn, r'\1', desc) if desc is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Shopbop(Retailer):
    name = "shopbop.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.shopbop.com/"
    structure = [
        {
            "units": "#pdp > div.pdp-desktop.pdp-shopbop",
            "targets": {
                "retailer_brand": "#product-title",
                "retailer_title": "#product-title",
                "retailer_description": "#long-description",
                "retailer_price": "#pdp-pricing > span.pdp-price",
                "retailer_origin_price": "div.flexboxgrid2__col-xs-12___2AWtWi_Cud.flexboxgrid2__col-sm-6___3WUSoaaPMC.flexboxgrid2__col-lg-5___2Hm1RWYupR > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > strong > div > span",
                "retailer_sku": "#long-description > div.product-code > span",
                "retailer_images": ("#pdp-image-main .display-list-item > img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Nugnes1920(Retailer):
    name = "nugnes1920.com"
    keyword = ""
    html = None
    TOP_URL = "https://us.nugnes1920.com/"
    structure = [
        {
            "units": "#shopify-section-product-template > div > div",
            "targets": {
                "retailer_brand": "div.product-page__info > div > div > div.product-page__main-data.product-page__main-data--hidden-xs > div:nth-child(1) > p.product-page__vendor > span > a",
                "retailer_title": "div.product-page__info > div > div > div.product-page__main-data.product-page__main-data--hidden-xs > div.product-page__line.js-wishlist > h1",
                "retailer_description": "div.product-page__info > div > div > div.product-page__materials",
                "retailer_price": "div.product-page__info > div > div > div.product-page__main-data.product-page__main-data--hidden-xs > div:nth-child(1) > p.product-page__price > span.price > span > span",
                "retailer_origin_price": "div.product-page__info > div > div > div.product-page__main-data.product-page__main-data--hidden-xs > div:nth-child(1) > p.product-page__price > span.price > span > span",
                "retailer_sku": "div.product-page__info > div > div > div.product-page__sku",
                "retailer_images": ("#imageLayer .gallery .gallery__image-container img", "data-src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        ptn = r"^.*Code:(.+)$"
                        desc = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        sku = re.sub(ptn, r'\1', desc) if desc is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Harveynichols(Retailer):
    name = "harveynichols.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.harveynichols.com/"
    structure = [
        {
            "units": "#page",
            "targets": {
                "retailer_brand": "div.p-details > div > p > a",
                "retailer_title": "div.p-details > div > div.p-details__name-wrap > h1 > p.p-details__name",
                "retailer_description": "div.p-more-info__inner > div.long-text > div",
                "retailer_price": "div.p-details > div > div.p-details__price > div > p",
                "retailer_origin_price": "div.p-details > div > div.p-details__price > div > p",
                "retailer_sku": "div.sku-style-number > p:nth-child(1) > span",
                "retailer_images": (".slick-slider .slick-list .slick-track > div > div > img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Tessabit(Retailer):
    name = "tessabit.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.tessabit.com/"
    structure = [
        {
            "units": "body",
            "targets": {
                "retailer_brand": "#product_addtocart_form > a > span",
                "retailer_title": "#product_addtocart_form > div.product-name > h1",
                "retailer_description": "#product_addtocart_form > div.description",
                "retailer_price": ".price-info > .price-box > span:nth-child(1) span.price",
                "retailer_origin_price": ".price-info > .price-box > span:nth-child(2) span.price",
                "retailer_sku": "#product_addtocart_form > div.description > div > span:nth-child(2)",
                "retailer_images": ("#product-gallery .product-gallery-carousel .owl-stage .owl-item img.img-responsive", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Matchesfashion(Retailer):
    name = "matchesfashion.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.matchesfashion.com/"
    structure = [
        {
            "units": "#pdpMainWrapper",
            "targets": {
                "retailer_brand": "div.pdp__description-wrapper > div.pdp__header.hidden-mobile > h1 > a",
                "retailer_title": "div.pdp__description-wrapper > div.pdp__header.hidden-mobile > h1 > span",
                "retailer_description": "#mCSB_1_container > div",
                "retailer_price": "div.pdp__description-wrapper > div.pdp__header.hidden-mobile > p",
                "retailer_origin_price": "div.pdp__description-wrapper > div.pdp__header.hidden-mobile > p",
                "retailer_sku": "#mCSB_1_container > div > p:nth-child(4) > span",
                "retailer_images": ("#main-image-js .slick-list .slick-slide > div > div > img:nth-child(1)", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Biffi(Retailer):
    name = "biffi.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.biffi.com/"
    structure = [
        {
            "units": "#maincontent > div.columns",
            "targets": {
                "retailer_brand": "div > div.product-info-main > div > div.top-block > div > div.pre-name > a",
                "retailer_title": "div > div.product-info-main > div > div.top-block > div > div.wrap-name-wishlist > h1",
                "retailer_description": "#tab-description > div",
                "retailer_price": "span.normal-price span.price",
                "retailer_origin_price": "span.old-price span.price",
                "retailer_sku": "#tab-description > div > div.product-sku > span",
                "retailer_images": (".images-gallery-wrapper .images-gallery > img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        sku = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Giglio(Retailer):
    name = "giglio.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.giglio.com/"
    structure = [
        {
            "units": "body > div.main > div",
            "targets": {
                "retailer_brand": "div.product__details > strong > a",
                "retailer_title": "div.product__details > h1",
                "retailer_description": "div.product__details > section.product_details",
                "retailer_price": "div.product__details > div.product__details__price > div > b",
                "retailer_origin_price": "div.product__details > div.product__details__price > div > b",
                "retailer_sku": "div.product__details > section.product_details > div > span",
                "retailer_images": (".product__images .prod-slider__slide > img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_sku":
                        # SKU 切り出し
                        "Designer code: "
                        ptn = r"^.*Designer code: (.+)Designer.+$"
                        desc = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        sku = re.sub(ptn, r'\1', desc) if desc is not None else None
                        _data.append(sku)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            i += 1
        return data, columns


class Gilt(Retailer):
    name = "gilt.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.gilt.com/"
    structure = [
        {
            "units": "#product_content",
            "targets": {
                "retailer_brand": "#product_header > h1:nth-child(1) > a",
                "retailer_title": "#product_header > h1:nth-child(2)",
                "retailer_description": "#sku_details_section",
                "retailer_price": "#product_header > div.price-box > span.pdp-list-price > span > span.value.bfx-price",
                "retailer_origin_price": "#product_header > div.price-box > span.pdp-msrp > a",
                "retailer_sku": "#product_header > h1:nth-child(2)",
                "retailer_images": ('//*[@id="thumbnail_images"]/a', "background",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

    def search(self, url: str = ""):
        """ search メソッド 
        指定したURLをリクエストし、
        HTMLソースを自身へセットする.
        """
        # 個別のアクションを追記
        self.driver.access(url)
        # 画像がcssのためプロパティを別途取得
        try:
            selector = self.get_structure("targets")["retailer_images"]
            images = self.driver._driver.find_elements_by_xpath(selector[0])
            img_urls = [img.value_of_css_property(selector[1]) for img in images]
            # //asset1.ruecdn.com/images/product/111120/1111209342_RLLA_1.jpg を https://asset1.ruecdn.com/images/product/111120/1111209342_RLLD_1.jpg へ変換
            ptn = r"^.*url\(\"(.+)\"\).*$"
            img_urls = [re.sub(ptn, r"\1", img_url).replace("_RLLA_", "_RLLD_") for img_url in img_urls]
            self.img_urls = "@@@".join(img_urls)
        except Exception as e:
            print("Exception Occured ... ", e.args[0])
            self.img_urls = None

        # HTML を取得
        self.html = self.driver.get_html()

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
                    if target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_images":
                        _data.append(self.img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Articture(Retailer):
    name = "articture.com"
    keyword = ""
    html = None
    TOP_URL = "https://articture.com/"
    structure = [
        {
            "units": "#shopify-section-product-template > section > div",
            "targets": {
                "retailer_brand": "",
                "retailer_title": "h1.ProductMeta__Title",
                "retailer_description": ".ProductMeta__Description",
                "retailer_price": "span.pro_main_price",
                "retailer_origin_price": "span.Price--compareAt",
                "retailer_sku": "",
                "retailer_images": ("img#ProductPhotoImg", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Requests()

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
                    if target == "retailer_brand" or target == "retailer_sku":
                        _data.append("Articture")
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append("")                            
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        if price is not None:
                            _data.append(price.get_text().strip())
                        else:
                            _data.append(None)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Antonioli(Retailer):
    name = "articture.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.antonioli.eu/"
    structure = [
        {
            "units": "#product-container",
            "targets": {
                "retailer_brand": "div.details.fixed > div.box-add > form > div.details--name > a",
                "retailer_title": "div.details.fixed > div.box-add > form > div.details--descriptions > div.details--descriptions--product > span",  # span の一行目のみ
                "retailer_description": "div.details.fixed > div.box-add > form > div.details--descriptions > div.details--descriptions--product > span",
                "retailer_price": ("div.details.fixed > div.box-add > form > div.details--price > div > span:nth-child(1)", "content",),
                "retailer_origin_price": "div.details.fixed > div.box-add > form > div.details--price > div > span:nth-child(1) > span > s",
                "retailer_sku": "",
                "retailer_images": ("div.images > div.images-extended > span", "data-image",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Requests()

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
                    if target == "retailer_title":
                        # 一行目のみ取得
                        title = unit.select_one(selector) if unit.select_one(selector) is not None else ""
                        if title is not None:
                            _data.append("\n".split(title)[0])
                        else:
                            _data.append("")                            
                    elif target == "retailer_sku":
                        # brand + title を sku に設定
                        _selector = self.get_structure("targets")["retailer_brand"]
                        _brand = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""
                        # 一行目のみ取得
                        _selector = self.get_structure("targets")["retailer_title"]
                        _title = "\n".split(unit.select_one(_selector))[0] if unit.select_one(_selector) is not None else ""
                        _data.append(_brand + " " + _title)
                    elif target == "retailer_price":
                        # SALE price がなければ OriginPrice を入れる
                        price = unit.select_one(selector[0])[selector[1]] if unit.select_one(selector[0]) is not None else None
                        if price is not None:
                            _data.append(price.strip())
                        else:
                            _selector = self.get_structure("targets")["retailer_origin_price"]
                            _data.append(unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else None)
                    elif target == "retailer_origin_price":
                        # Old price がなければ Price を入れる
                        origin_price = unit.select_one(selector) if unit.select_one(selector) is not None else None
                        if origin_price is not None:
                            _data.append(origin_price.get_text().strip())
                        else:
                            _selector = self.get_structure("targets")["retailer_price"]
                            origin_price = unit.select_one(_selector[0])[1] if unit.select_one(_selector[0]) is not None else None
                            _data.append(origin_price)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class _24scom(Retailer):
    name = "24s.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.24s.com/"
    structure = [
        {
            "units": "#__next",
            "targets": {
                "retailer_brand": "h1.item-product > a.item-brand",
                "retailer_title": "h1.item-product > span",
                "retailer_description": "div.b-quote > blockquote",
                "retailer_price": "h1 ~ div.item-price p:nth-child(1) > span",
                "retailer_origin_price": "h1 ~ div.item-price p.sale",
                "retailer_sku": "",
                "retailer_images": (".slick-slider.slick-horizontal > .slick-list > .slick-track > .slick-slide img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

    def search(self, url: str = ""):
        """ 汎用 search メソッド 
        指定したURLをリクエストし、
        HTMLソースを自身へセットする.
        """
        # 個別のアクションを追記
        self.driver.access(url)
        self.driver.wait()

        # slick_slider 部分を事前にクリックする
        script = '$.each($(".slick-slider.slick-vertical > .slick-list > .slick-track > .slick-slide"), function(i, elm){setTimeout(function(){ $(".slick-arrow.slick-next").click() }, i * 1000)})'
        self.driver._driver.execute_script(script)

        # HTML を取得
        self.html = self.driver.get_html()

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
                    if target == "retailer_sku":
                        # brand + title を sku に設定
                        _selector = self.get_structure("targets")["retailer_brand"]
                        _brand = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _selector = self.get_structure("targets")["retailer_title"]
                        _title = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _data.append(_brand + " " + _title)
                    elif target == "retailer_price":
                        # ¥17,680 /€141 の形で入ってくるためトリミング
                        ptn = r"(¥[0-9\.,]+).*/.+$"
                        price = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else ""
                        price = re.sub(ptn, r"\1", price)
                        _data.append(price)
                    elif target == "retailer_origin_price":
                        origin_price = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None
                        # retailer_origin_price がなければ retailer_price を入れる
                        if origin_price is None:
                            origin_price = unit.select_one(self.get_structure("targets")["retailer_price"]).get_text().strip() if unit.select_one(self.get_structure("targets")["retailer_price"]) is not None else ""
                            # ¥17,680 /€141 の形で入ってくるためトリミング
                            ptn = r"(¥[0-9\.,]+).*/.+$"
                            origin_price = re.sub(ptn, r"\1", origin_price)
                        else:
                            # (was ¥22,100) -20% の形で入ってくるためトリミング
                            ptn = r"(¥[0-9\.,]+).*/.+$"
                            origin_price = re.sub(ptn, r"\1", origin_price)
                        _data.append(origin_price)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Modaoperandi(Retailer):
    name = "modaoperandi.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.modaoperandi.com/"
    structure = [
        {
            "units": "#wraps-body-content",
            "targets": {
                "retailer_brand": (".product_detail_page", "data-brand",),
                "retailer_title": (".product_detail_page", "data-name",),
                "retailer_description": ".description_text.editors_note_text > p",
                "retailer_price": ".product_price span.current_price",
                "retailer_origin_price": ".product_price span.original_price",
                "retailer_sku": "",  # 一応 SKU も .product_code としてあるが作成する
                "retailer_images": (".pdp_image_wrapper img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    if target == "retailer_brand":
                        _data.append(unit.select_one(selector[0])[selector[1]].strip() if unit.select_one(selector[0]) is not None else None)
                    elif target == "retailer_title":
                        _data.append(unit.select_one(selector[0])[selector[1]].strip() if unit.select_one(selector[0]) is not None else None)
                    elif target == "retailer_sku":
                        # brand + title を sku に設定
                        _selector = self.get_structure("targets")["retailer_brand"]
                        _brand = unit.select_one(_selector[0])[_selector[1]].strip() if unit.select_one(_selector[0]) is not None else ""

                        _selector = self.get_structure("targets")["retailer_title"]
                        _title = unit.select_one(_selector[0])[_selector[1]].strip() if unit.select_one(_selector[0]) is not None else ""

                        _data.append(_brand + " " + _title)
                    elif target == "retailer_origin_price":
                        # retailer_origin_price がなければ retailer_price を入れる
                        origin_price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"])
                        origin_price = origin_price.get_text().strip() if origin_price is not None else None
                        _data.append(origin_price)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Danielloboutique(Retailer):
    name = "danielloboutique.it"
    keyword = ""
    html = None
    TOP_URL = "https://www.danielloboutique.it/"
    structure = [
        {
            "units": "#maincontent",
            "targets": {
                "retailer_brand": ".product.attribute.manufacturer > div",
                "retailer_title": ".product.attribute.name > div",
                "retailer_description": ".product.attribute.description > div.content",
                "retailer_price": ".product-info-main .price-box > span span.price",
                "retailer_origin_price": ".product-info-main .price-box span.old-price span.price",
                "retailer_sku": "",  # 一応 SKU も .product_code としてあるが作成する
                "retailer_images": ("img.fotorama__img", "src",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

    def search(self, url: str = ""):
        """ 汎用 search メソッド 
        指定したURLをリクエストし、
        HTMLソースを自身へセットする.
        """
        # 個別のアクションを追記
        self.driver.access(url)
        selector = self.get_structure("targets")["retailer_images"][0]
        self.driver.wait(selector=selector)
        # HTML を取得
        self.html = self.driver.get_html()

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
                    if target == "retailer_sku":
                        # brand + title を sku に設定
                        _selector = self.get_structure("targets")["retailer_brand"]
                        _brand = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _selector = self.get_structure("targets")["retailer_title"]
                        _title = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _data.append(_brand + " " + _title)
                    elif target == "retailer_origin_price":
                        # retailer_origin_price がなければ retailer_price を入れる
                        origin_price = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_price"]).get_text().strip()
                        _data.append(origin_price)
                    elif target == "retailer_images":
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([img_url[selector[1]] for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Raffaellonetwork(Retailer):
    name = "raffaello-network.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.raffaello-network.com/"
    structure = [
        {
            "units": "#detail",
            "targets": {
                "retailer_brand": "#product-range > h1",
                "retailer_title": "#product-range > span",
                "retailer_description": "#features",
                "retailer_price": "#specialoffer",
                "retailer_origin_price": "#prices > span",
                "retailer_sku": "#features span:last-child",
                "retailer_images": ("#detail-left ul li a", "rel",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Requests()

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
                    if target == "retailer_price":
                        # retailer_price がなければ retailer_origin_price を入れる
                        price = unit.select_one(selector) if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"])
                        price = price.get_text().strip() if price is not None else None
                        _data.append(price)
                    elif target == "retailer_images":
                        # この形で入ってくるのでトリミング
                        # {gallery: 'gal1', smallimage: 'https://cdn.raffaello-network.com/english/fashion-details/465520/36/gucci-sunglasses_gucsun-gg0253s002002-medium-1.jpg',largeimage: 'https://cdn.raffaello-network.com/english/fashion-details/465520/36/gucci-sunglasses_gucsun-gg0253s002002-large-1.jpg'}
                        ptn = r".*largeimage:.*\'(http.+)\'.+$"
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        if any(img_urls):
                            urls = []
                            for img_url in img_urls:
                                if img_url.has_attr(selector[1]):
                                    attr = str(img_url[selector[1]])
                                    urls.append(re.sub(ptn, r"\1", attr))
                            img_urls = "@@@".join(urls)
                        else:
                            img_urls = None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns


class Saksfifthavenue(Retailer):
    name = "saksfifthavenue.com"
    keyword = ""
    html = None
    TOP_URL = "https://www.saksfifthavenue.com/"
    structure = [
        {
            "units": "#pdp-content-area",
            "targets": {
                "retailer_brand": ".product-overview__brand",
                "retailer_title": "h1.product-overview__short-description",
                "retailer_description": ".product-description",
                "retailer_price": "#salePrice",
                "retailer_origin_price": "#regularPrice",
                "retailer_sku": "",  # 一応 SKU も .product_code としてあるが作成する
                "retailer_images": ("div.s7thumb", "style",),
                # "colors": "",
                # "sizes": ""
            }
        }
    ]
    more_button = ""
    _term = 0  # structure の層数に合わせて振る舞いを変えるための現状層を示す
    max_term = 0

    def __init__(self, url:str=""):
        self.url = url
        self.driver = Chrome()

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
                    if target == "retailer_sku":
                        # brand + title を sku に設定
                        _selector = self.get_structure("targets")["retailer_brand"]
                        _brand = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _selector = self.get_structure("targets")["retailer_title"]
                        _title = unit.select_one(_selector).get_text().strip() if unit.select_one(_selector) is not None else ""

                        _data.append(_brand + " " + _title)
                    elif target == "retailer_price":
                        # retailer_price がなければ retailer_origin_price を入れる
                        price = unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else unit.select_one(self.get_structure("targets")["retailer_origin_price"]).get_text().strip()
                        _data.append(price)
                    elif target == "retailer_images":
                        # style属性で入ってくるのでトリミング
                        # background-repeat: no-repeat; background-position: center center; width: 76px; height: 90px; background-image: url("https://image.s5a.com/is/image/saks/0400011817797_A3?fit=constrain,1&wid=76&hei=90&fmt=jpg&op_usm%3D1.2%2C1%2C10%2C0%26resmode%3Dsharp%26iccEmbed%3d1%26icc%3DsRGB%20IEC61966-2.1%26op_saturation%3D-15");
                        ptn = r"^.+url\(\"(http.+)\?.+\"\).*$"  # 原サイズを取りたいので ? 以降を除去
                        img_urls = unit.select(selector[0]) if any(unit.select(selector[0])) else []
                        img_urls = "@@@".join([re.sub(ptn, r"\1", img_url[selector[1]]) for img_url in img_urls]) if any(img_urls) else None
                        _data.append(img_urls)
                    else:
                        _data.append(unit.select_one(selector).get_text().strip() if unit.select_one(selector) is not None else None)
            data[i] = _data
            print(self.name, _data)
            i += 1
        return data, columns

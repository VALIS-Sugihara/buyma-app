from ec._client import Client
from ec.channels.curators import Lyst, Shoppingscanner, Articture as Art
from ec.channels.retailers import (
    Ruelala, Mytheresa, Farfetch, Vitkac, Modes, Forzieri, Mybag, Coggles, Cettire, Ssense, Luisaviaroma,
    Shopbop, Nugnes1920, Harveynichols, Tessabit, Matchesfashion, Biffi, Giglio, Gilt, Articture,
    Antonioli, _24scom, Modaoperandi, Danielloboutique, Raffaellonetwork, Saksfifthavenue,
    Saksoff5th
)
from ec.channels.malls import BuymaItems

import pandas as pd
import re

RETAILER_NAMES = (
    "Ruelala", "Mytheresa", "Farfetch", "Vitkac", "Modes", "Forzieri", "Mybag", "Coggles", "Cettire", "Ssense", "Luisaviaroma",
    "Shopbop", "Nugnes1920", "Harveynichols", "Tessabit", "Matchesfashion", "Biffi", "Giglio", "Gilt", "Articture",
    "Antonioli", "_24scom", "Modaoperandi", "Danielloboutique", "Raffaellonetwork", "Saksfifthavenue",
    "Saksoff5th"
)


import unittest


class TestRetailers(unittest.TestCase):
    # TODO:: self.name == "name" assert

    def test_Ruelala(self):
        url = "https://www.ruelala.com/boutique/product/159083/100976374/?dsi=BTQ--3789916f-f5d9-4482-8035-829886aedae5&lsi=146e8ffd-6e44-4657-a80e-262984805ab1&pos=1"
        retailer = Ruelala(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Mytheresa(self):
        url = "https://www.mytheresa.com/en-jp/valentino-wool-blend-crepe-dress-1363812.html?catref=category"
        retailer = Mytheresa(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Farfetch(self):
        url = "https://www.farfetch.com/jp/shopping/women/jil-sander--item-14829276.aspx?storeid=9359"
        retailer = Farfetch(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Vitkac(self):
        url = "https://www.vitkac.com/us/p/training-sneakers-ea7-emporio-armani-shoes-1081759"
        retailer = Vitkac(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Modes(self):
        # robots
        # try:
        #     url = "https://www.modes.com/jp/shopping/dg-amore-tote-bag-15108866"
        #     retailer = Modes(url)
        #     c = Client(retailer)
        #     c.search()
        #     data, columns = c.collect()

        #     self.assertIsInstance(data, dict)
        #     self.assertNotIn(None, data[0])

        # except:
        #     c.channel.driver.screenshot("/tmp/Modes.png")
        pass

    def test_Forzieri(self):
        url = "https://www.jp.forzieri.com/jpn/product_view.asp?l=jpn&c=jpn&pkb=1&dept_id=18&sku=mx130620-018-00"
        retailer = Forzieri(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Mybag(self):
        # キャプチャ発生
        # url = "https://www.mybag.com/bags-clothing-women-accessories/coach-women-s-charlie-40-carryall-bag-heather-grey/12519561.html"
        # retailer = Mybag(url)
        # c = Client(retailer)
        # c.search()
        # data, columns = c.collect()

        # print(data)

        # self.assertIsInstance(data, dict)
        # self.assertNotIn(None, data[0])
        pass

    def test_Coggles(self):
        url = "https://www.coggles.com/bags-clothing-women-accessories/by-far-women-s-amber-snake-print-bag-snake-print/12490621.html"
        retailer = Coggles(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Cettire(self):
        url = "https://www.cettire.com/collections/ss20-sale/products/valentino-side-stripe-pants-93191167"
        retailer = Cettire(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Ssense(self):
        url = "https://www.ssense.com/ja-us/women/product/balenciaga/pink-baguette-bag/5116701"
        retailer = Ssense(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Luisaviaroma(self):
        try:
            url = "https://www.luisaviaroma.com/ja-jp/p/neil-barrett/%E3%83%A1%E3%83%B3%E3%82%BA/%E3%82%B7%E3%83%A7%E3%83%BC%E3%83%88%E3%83%91%E3%83%B3%E3%83%84/71I-05I009?ColorId=NTI00&SubLine=clothing&CategoryId=109&lvrid=_p_d106_gm_c109"
            retailer = Luisaviaroma(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Luisa.png")

    def test_Shopbop(self):
        url = "https://www.shopbop.com/emma-dress-rixo/vp/v=1/1587287985.htm?folderID=13594&fm=other-shopbysize-viewall&os=false&colorId=182D2&ref_=SB_PLP_EP_1"
        retailer = Shopbop(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Nugnes1920(self):
        url = "https://us.nugnes1920.com/collections/sale-man/products/lardini_jacket_blue_eiljm56ei54000-850"
        retailer = Nugnes1920(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Harveynichols(self):
        try:
            url = "https://www.harveynichols.com/int/brand/tl-180/379088-le-fazzoletto-snake-effect-top-handle-bag/p3747340/"
            retailer = Harveynichols(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])
        except:
            c.channel.driver.screenshot("/tmp/Harvey.png")

    def test_Tessabit(self):
        try:
            url = "https://www.tessabit.com/jp/woman-fendi-jackets-belted-jacket-847587295/"
            retailer = Tessabit(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])
        except:
            c.channel.driver.screenshot("/tmp/Tessabit.png")

    def test_Matchesfashion(self):
        try:
            url = "https://www.matchesfashion.com/en-jp/products/Paul-Smith-Leather-bi-fold-wallet-1241440"
            retailer = Matchesfashion(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Matches.png")

    def test_Biffi(self):
        url = "https://www.biffi.com/it_it/sandali-bv-board-item-000258750038277.html"
        retailer = Biffi(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Giglio(self):
        # robot チェック
        # try:
        #     url = "https://www.giglio.com/eng/shoes-women_high-heel-shoes-shoes-women-bottega-veneta-630148vbp40.html?cSel=090"
        #     retailer = Giglio(url)
        #     c = Client(retailer)
        #     c.search()
        #     data, columns = c.collect()

        #     # print(data)

        #     self.assertIsInstance(data, dict)
        #     self.assertNotIn(None, data[0])

        # except:
        #     c.channel.driver.screenshot("/tmp/Giglio.png")
        pass

    def test_Gilt(self):
        try:
            url = "https://www.gilt.jp/sales/114191467/looks/114361585?size=38"
            retailer = Gilt(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Gilt.png")

    def test_Articture(self):
        url = "https://articture.com/collections/best-sellers/products/light-of-life?variant=23168128843834"
        retailer = Articture(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Antonioli(self):
        # 取得不可
        # url = "https://www.antonioli.eu/ja/JP/women/products/bb50f6b0u0-404"
        # retailer = Antonioli(url)
        # c = Client(retailer)
        # c.search()
        # data, columns = c.collect()

        # # print(data)

        # self.assertIsInstance(data, dict)
        # self.assertNotIn(None, data[0])
        pass

    def test__24scom(self):
        url = "https://www.24s.com/en-jp/zoom-x-vista-grind-trainers-nike_NIK7ENKP?defaultSku=NIK7ENKPBLUNI08500&color=fossil-stone-sail-hyper-blue"
        retailer = _24scom(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Modaoperandi(self):
        try:
            url = "https://www.modaoperandi.com/jil-sander-fw20/grande-tangle-leather-tote?size=OS"
            retailer = Modaoperandi(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Modaoperand.png")
            

    def test_Danielloboutique(self):
        try:
            url = "https://www.danielloboutique.it/jp/catalog/product/view/id/93802/s/4263943/category/314/"
            retailer = Danielloboutique(url)
            c = Client(retailer)
            c.search()

            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Danielloboutique.png")

    def test_Raffaellonetwork(self):
        url = "https://www.raffaello-network.com/japanese/fashion-detail/569101/28/%E3%83%97%E3%83%A9%E3%83%80%20%E3%83%A1%E3%83%B3%E3%82%BA%E3%80%80%E3%82%B7%E3%83%A5%E3%83%BC%E3%82%BA.html"
        retailer = Raffaellonetwork(url)
        c = Client(retailer)
        c.search()
        data, columns = c.collect()

        # print(data)

        self.assertIsInstance(data, dict)
        self.assertNotIn(None, data[0])

    def test_Saksfifthavenue(self):
        try:
            url = "https://www.saksfifthavenue.com/3-1-phillip-lim-drum-leather-ankle-boots/product/0400099230689?R=888824640622&P_name=3.1+Phillip+Lim&N=1553"
            retailer = Saksfifthavenue(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Saksfifthavenue.png")

    def test_Saksoff5th(self):
        try:
            url = "https://www.saksoff5th.com/product/marcus-adler-printed-2-piece-bandana-mask-set-0400012781189.html?dwvar_0400012781189_color=RED_BLUE"
            retailer = Saksoff5th(url)
            c = Client(retailer)
            c.search()
            data, columns = c.collect()

            # print(data)

            self.assertIsInstance(data, dict)
            self.assertNotIn(None, data[0])

        except:
            c.channel.driver.screenshot("/tmp/Saksfifthavenue.png")


if __name__ == '__main__':
    # unittest.main()
    t = TestRetailers()
    t.test_Saksoff5th()
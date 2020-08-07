from ec._client import Client
from ec.channels.curators import Lyst, Shoppingscanner, Articture as Art
from ec.channels.retailers import Ruelala, Mytheresa, Farfetch, Vitkac, Modes, Forzieri, Mybag, Coggles, Cettire, Ssense, Luisaviaroma, Shopbop, Nugnes1920, Harveynichols, Tessabit, Matchesfashion, Biffi, Giglio, Gilt, Articture
from ec.channels.malls import BuymaItems

import pandas as pd
import re

RETAILER_NAMES = (
    "Ruelala", "Mytheresa", "Farfetch", "Vitkac", "Modes", "Forzieri", "Mybag", "Coggles", "Cettire", "Ssense", "Luisaviaroma",
    "Shopbop", "Nugnes1920", "Harveynichols", "Tessabit", "Matchesfashion", "Biffi", "Giglio", "Gilt", "Articture"
)


def exchange_currency(cheapest_price: str):
    prc_ptn = r"[^0-9\.]"
    if "€" in cheapest_price:
        # cheapest_price = float(cheapest_price.replace("€", "").replace(",", "").strip()) * 120
        cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 120
    elif "£" in cheapest_price:
        # cheapest_price = float(cheapest_price.replace("£", "").replace(",", "").strip()) * 135
        cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 135
    elif "$" in cheapest_price or "USD" in cheapest_price:
        # cheapest_price = float(cheapest_price.replace("$", "").replace(",", "").strip()) * 108
        cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 108
    elif "¥" in cheapest_price or "JPY" in cheapest_price or "￥" in cheapest_price:
        # cheapest_price = float(cheapest_price.replace("¥", "").replace("JPY", "").replace(",", "").strip())
        cheapest_price = float(re.sub(prc_ptn, "", cheapest_price))

    return cheapest_price


def test(event, context):
    keywords = ["goyard", "bag"]

    """ Lyst から検索ワード一覧を取得 """

    lyst = Lyst()
    c = Client(lyst)
    c.search(keywords=keywords, discount_rate=20)
    data, columns = c.collect()
    # print(data)
    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/Lyst.com&celine+bag.collected.csv"

    df_curator = pd.read_csv(path)
    print(df_curator.head())

    """ 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        retailer_name = row["retailer"].replace(" ", "").capitalize().strip()
        if retailer_name in RETAILER_NAMES:
            retailer = globals()[retailer_name](row["href"])
            c = Client(retailer)
            c.search()
            data, columns = c.collect()
            print(data)
            try:
                data_dict[index] = data[0]
            except KeyError:
                data_dict[index] = [None for c in columns]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    retailer_df = c.to_df(data=data_dict, columns=columns, save=path)

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, retailer_df], axis=1)
    df2.to_csv(path)

    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    buymaItems = BuymaItems()

    """ 取得先のリテーラーから必要情報を取得 """

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    prc_ptn = r"[^0-9\.]"
    active_dict = {}
    for index, row in df2.iterrows():
        sku = re.sub(ptn, r"\1", row["retailer_sku"])
        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通過" があるので str 型にしておく

        cheapest_price = exchange_currency(cheapest_price)

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = [BuymaItems.compare(cheapest_price, prices), cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)
    # mall_df = pd.DataFrame.from_dict(active_dict, orient="index", columns=["active"])
    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


def sub(event, context):
    keywords = ["GOYARD"]

    """ Lyst から検索ワード一覧を取得 """

    shoppingscanner = Shoppingscanner()
    c = Client(shoppingscanner)
    c.search(keywords=keywords)
    data, columns = c.collect()
    print(data)
    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/Shoppingscanner.com&balenciaga+wallet.collected.csv"

    df_curator = pd.read_csv(path)
    print(df_curator.head())
    # df_curator = df_curator.head()

    """ 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer_name = row["retailer"].replace("AT", "").replace(" ", "").capitalize().strip()
            if retailer_name in RETAILER_NAMES:
                retailer = globals()[retailer_name](row["href"])
                c = Client(retailer)
                c.search()
                data, columns = c.collect()
                print(data)
                try:
                    data_dict[index] = data[0]
                except KeyError:
                    data_dict[index] = [None for c in columns]
        except Exception as e:
            print("...Exception Occured...", index, row["title"])
            print(e.args[0])
            data_dict[index] = [None for c in columns]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    # print(data_dict)
    retailer_df = c.to_df(data=data_dict, columns=columns, save=path)

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    # path = "~/Desktop/gilt.com&celine+wallet+strap.curator-retailer.csv"
    df2 = pd.concat([df_curator, retailer_df], axis=1)
    df2.to_csv(path)

    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    buymaItems = BuymaItems()

    """ 取得先のリテーラーから必要情報を取得 """

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    prc_ptn = r"[^0-9\.]"
    active_dict = {}
    for index, row in df2.iterrows():
        sku = re.sub(ptn, r"\1", row["retailer_sku"])
        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通過" があるので str 型にしておく

        cheapest_price = exchange_currency(cheapest_price)

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = [BuymaItems.compare(cheapest_price, prices), cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)
    # mall_df = pd.DataFrame.from_dict(active_dict, orient="index", columns=["active"])
    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


def articture(event, context):
    keywords = ["set"]

    """ 結果一覧を取得 """

    artiic = Art()
    c = Client(artiic)
    data_dict = {}

    while c.channel.next_page is not None:
        c.search(keywords=keywords)
        data, columns = c.collect()
        data_dict.update(data)
    print(data)
    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data_dict, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/articture.com&light.collected.csv"

    df_curator = pd.read_csv(path)
    print(df_curator.head())
    # df_curator = df_curator.head()

    """ 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer = Articture(row["href"])
            c = Client(retailer)
            c.search()
            data, columns = c.collect()
            print(data)
            try:
                data_dict[index] = data[0]
            except KeyError:
                data_dict[index] = [None for c in columns]
        except Exception as e:
            print("...Exception Occured...", index, row["title"])
            print(e.args[0])
            data_dict[index] = [None for c in columns]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    # print(data_dict)
    retailer_df = c.to_df(data=data_dict, columns=columns, save=path)

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, retailer_df], axis=1)
    df2.to_csv(path)

    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    # buymaItems = BuymaItems()

    """ 取得先のリテーラーから必要情報を取得 """

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    prc_ptn = r"[^0-9\.]"
    active_dict = {}
    for index, row in df2.iterrows():
        # sku = re.sub(ptn, r"\1", row["retailer_sku"])
        cheapest_price = row["retailer_price"]

        cheapest_price = exchange_currency(cheapest_price)

        active_dict[index] = [1, cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)
    # mall_df = pd.DataFrame.from_dict(active_dict, orient="index", columns=["active"])
    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


test(1,1)

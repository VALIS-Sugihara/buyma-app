from ec._client import Client
from ec.channels.curators import (
    Lyst, Shoppingscanner, Articture as Art, DolceAndGabbana
)
from ec.channels.retailers import (
    Ruelala, Mytheresa, Farfetch, Vitkac, Modes, Forzieri, Mybag, Coggles, Cettire, Ssense, Luisaviaroma,
    Shopbop, Nugnes1920, Harveynichols, Tessabit, Matchesfashion, Biffi, Giglio, Gilt, Articture,
    Antonioli, _24scom, Modaoperandi, Danielloboutique, Raffaellonetwork, Saksfifthavenue,
    Saksoff5th, Theluxurycloset, Dolcegabbana
)
from ec.channels.malls import BuymaItems

import pandas as pd
import re

RETAILER_NAMES = (
    "Ruelala", "Mytheresa", "Farfetch", "Vitkac", "Modes", "Forzieri", "Mybag", "Coggles", "Cettire", "Ssense", "Luisaviaroma",
    "Shopbop", "Nugnes1920", "Harveynichols", "Tessabit", "Matchesfashion", "Biffi", "Giglio", "Gilt", "Articture",
    "Antonioli", "_24scom", "Modaoperandi", "Danielloboutique", "Raffaellonetwork", "Saksfifthavenue",
    "Saksoff5th", "Theluxurycloset", "Dolcegabbana"
)


def exchange_currency(cheapest_price: str):
    prc_ptn = r"[^0-9\.]"
    try:
        if "€" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("€", "").replace(",", "").strip()) * 120
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 120
        elif "£" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("£", "").replace(",", "").strip()) * 135
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 135
        elif "$" in cheapest_price or "USD" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("$", "").replace(",", "").strip()) * 108
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 108
        elif "¥" in cheapest_price or "JPY" in cheapest_price or "￥" in cheapest_price or "円" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("¥", "").replace("JPY", "").replace(",", "").strip())
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price))
    except Exception as e:
        print("Exception is Occured...", e.args[0])
        cheapest_price = 99999999999

    return cheapest_price


def exchange_retailer_name(retailer_name: str):
    sub_ptn = r"[^a-zA-Z0-9]"
    check_ptn = r"^[0-9]"
    class_name = re.sub(sub_ptn, "", retailer_name.replace("AT ", "", 1)).capitalize()
    if re.match(check_ptn, class_name) is not None:
        class_name = "_" + class_name 

    return class_name


def test(event, context):
    keywords = ["celine", "bag"]
    discount_rate = 50

    """ Pt.1 Lyst から検索ワード一覧を取得 """

    # lyst = Lyst()
    # c = Client(lyst)
    # c.search(keywords=keywords, discount_rate=discount_rate)
    # data, columns = c.collect()
    # path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    # df_curator = c.to_df(data=data, columns=columns, save=path)

    # keywords = ["FURLA"]
    path = "~/Desktop/Lyst.com&celine+bag.collected.csv"
    df_curator = pd.read_csv(path)
    print(df_curator.head())

    """ Pt.2 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer_name = exchange_retailer_name(row["retailer"])
            if retailer_name in RETAILER_NAMES:
                retailer = globals()[retailer_name](row["href"])
                c = Client(retailer)
                c.search()
                data, columns = c.collect()
                try:
                    data_dict[index] = data[0]
                except KeyError:
                    data_dict[index] = [None for c in columns]
        except Exception as e:
            print("...Exception Occured...", index, row["title"])
            print(e.args[0])
            data_dict[index] = [None for c in columns]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    df_retailer = c.to_df(data=data_dict, columns=columns, save=path)

    """ Pt.3 キュレーターとリテーラーを結合 """

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, df_retailer], axis=1)
    df2.to_csv(path)
    # df2 = pd.read_csv(path)
    df2 = df2.dropna()

    """ Pt.4 BUYMA で価格チェック """

    buymaItems = BuymaItems()

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    active_dict = {}
    for index, row in df2.iterrows():
        # SKU を検索ワードに設定
        sku = re.sub(ptn, r"\1", row["retailer_sku"])

        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通貨" があるので str 型にしておく
        cheapest_price = exchange_currency(cheapest_price)

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = [BuymaItems.compare(cheapest_price, prices), cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)

    """ Pt.5 リサーチ結果を結合し、1 のものだけをフィルター """

    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


def sub(event, context):
    keywords = ["gucci", "bag"]
    discount_rate = 0

    """ Pt.1 Lyst から検索ワード一覧を取得 """

    shoppingscanner = Shoppingscanner()
    c = Client(shoppingscanner)
    c.search(keywords=keywords, discount_rate=discount_rate)
    data, columns = c.collect()
    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/Shoppingscanner.com&loewe+bag.collected.csv"
    # df_curator = pd.read_csv(path)
    print(df_curator.head())

    """ Pt.2 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer_name = exchange_retailer_name(row["retailer"])
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
    df_retailer = c.to_df(data=data_dict, columns=columns, save=path)

    """ Pt.3 キュレーターとリテーラーを結合 """

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, df_retailer], axis=1)
    df2.to_csv(path)
    # path = "~/Desktop/saksfifthavenue.com&valentino.curator-retailer.csv"
    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    
    """ Pt.4 BUYMA で価格チェック """

    buymaItems = BuymaItems()

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    active_dict = {}
    for index, row in df2.iterrows():
        # SKU を検索ワードに設定
        sku = re.sub(ptn, r"\1", row["retailer_sku"])

        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通貨" があるので str 型にしておく
        cheapest_price = exchange_currency(cheapest_price)

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = [BuymaItems.compare(cheapest_price, prices), cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)

    """ Pt.5 リサーチ結果を結合し、1 のものだけをフィルター """

    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


def articture(event, context):
    keywords = ["set"]

    """ Pt.1 Articture の検索結果一覧を取得 """

    artic = Art()
    c = Client(artic)

    data_dict = {}
    while c.channel.next_page is not None:
        c.search(keywords=keywords)
        data, columns = c.collect()
        data_dict.update(data)

    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data_dict, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/articture.com&light.collected.csv"
    # df_curator = pd.read_csv(path)
    print(df_curator.head())

    """ Pt.2 取得先の href リンク先から必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer = Articture(row["href"])
            c = Client(retailer)
            c.search()
            data, columns = c.collect()
            try:
                data_dict[index] = data[0]
            except KeyError:
                data_dict[index] = [None for c in columns]
        except Exception as e:
            print("...Exception Occured...", index, row["title"])
            print(e.args[0])
            data_dict[index] = [None for c in columns]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    df_retailer = c.to_df(data=data_dict, columns=columns, save=path)

    """ Pt.3 キュレーターとリテーラーを結合 """

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, df_retailer], axis=1)
    df2.to_csv(path)
    # df2 = pd.read_csv(path)
    df2 = df2.dropna()

    """ Pt.4 BUYMA で価格チェック（出品がないためスキップ） """

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    active_dict = {}
    for index, row in df2.iterrows():
        # SKU を検索ワードに設定
        # sku = re.sub(ptn, r"\1", row["retailer_sku"])

        cheapest_price = row["retailer_price"]
        cheapest_price = exchange_currency(cheapest_price)

        active_dict[index] = [1, cheapest_price]  # 全て アクティブ 1 に設定

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)

    """ Pt.5 リサーチ結果を結合し、1 のものだけをフィルター """

    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


def dandg(event, context):
    keywords = ["bag"]

    """ Pt.1 Lyst から検索ワード一覧を取得 """

    dg = DolceAndGabbana()
    c = Client(dg)
    c.search(keywords=keywords)
    data, columns = c.collect()
    path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    df_curator = c.to_df(data=data, columns=columns, save=path)

    # keywords = ["FURLA"]
    # path = "~/Desktop/Shoppingscanner.com&loewe+bag.collected.csv"
    # df_curator = pd.read_csv(path)
    print(df_curator.head())

    """ Pt.2 取得先のリテーラーから必要情報を取得 """

    data_dict = {}
    for index, row in df_curator.iterrows():
        try:
            retailer_name = exchange_retailer_name(row["retailer"])
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
    df_retailer = c.to_df(data=data_dict, columns=columns, save=path)

    """ Pt.3 キュレーターとリテーラーを結合 """

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, df_retailer], axis=1)
    df2.to_csv(path)
    # path = "~/Desktop/dolcegabbana.com&bag.curator-retailer.csv"
    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    
    """ Pt.4 BUYMA で価格チェック """

    buymaItems = BuymaItems()

    # ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    active_dict = {}
    for index, row in df2.iterrows():
        # SKU を検索ワードに設定
        # sku = re.sub(ptn, r"\1", row["retailer_sku"])
        sku = row["retailer_sku"]

        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通貨" があるので str 型にしておく
        cheapest_price = exchange_currency(cheapest_price)

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = [BuymaItems.compare(cheapest_price, prices), cheapest_price]

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active", "active_price"], save=path)

    """ Pt.5 リサーチ結果を結合し、1 のものだけをフィルター """

    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True


sub(1,1)

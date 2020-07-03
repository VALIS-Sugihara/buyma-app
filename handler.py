import json
import boto3
import re

import constants
from ec.shop import Shop

# From Layer
import requests
from bs4 import BeautifulSoup
import pandas as pd

from aws.s3 import S3


def _get_event_data(event):
    return json.loads(json.dumps(event))


def hello(event, context):

    print(event)

    data = _get_event_data(event)
    response = requests.get(data["page"])
    soup = BeautifulSoup(response.text, 'html.parser')
    hrefs = [c["href"] for c in soup.select('p.buyeritem_name a')]
    titles = [c.get_text().strip() for c in soup.select('p.buyeritem_name a')]

    items = []

    for href, title in zip(hrefs, titles):
        items.append([href, title])

    print("hrefs is ...", hrefs)
    print("titles is ...", titles)

    print("items is ...", items)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def test(event, context):
    for shopper in constants.shopper_list:

        shop = Shop(shopper, ("Sales",))

        # payload = json.dumps(event)

        # for i in range(1, 10 + 1):
        for i in range(1, shop.sales.total_page + 1):
            # url = shop.get_sales_now_url(i)
            SALES_URL = "https://www.buyma.com/buyer/%s/sales_%s.html"
            url = SALES_URL % (shop.id, str(i),)
            payload = {
                "name": shop.name,
                "id": shop.id,
                "url": url
            }
            payload = json.dumps(payload)
            print(payload)
            response = boto3.client('lambda').invoke(
                FunctionName='buyma-app-dev-getItemList',
                InvocationType='Event',  # Event or RequestResponse
                Payload=payload
            )

    return response["Payload"].read().decode("utf-8")


def get_shopper(event, context):

    data = _get_event_data(event)
    shop_name = data["name"]

    pkl_name = "%s.pkl" % (shop_name,)

    s3 = S3(bucket_name=constants.S3_BUCKET)
    response = s3.download_item(key="shoppers/%s" % (pkl_name,), path="/tmp/%s" % (pkl_name,))

    print(response)

    pkl_obj = pd.read_pickle("/tmp/%s" % (pkl_name,))

    print(pkl_obj)

    return True


def save_shoppers(event, context):

    for shopper in constants.shopper_list:
        shop = Shop(shopper, ("Sales",))
        pkl_name = "%s.pkl" % (shop.name,)
        pd.to_pickle(shop, "/tmp/" + pkl_name)
        pkl_obj = open("/tmp/" + pkl_name, "rb")

        s3 = S3(bucket_name=constants.S3_BUCKET)
        response = s3.upload_item(key="shoppers/%s" % (pkl_name,), item=pkl_obj)

        print(response)

    return True

    # payload = json.dumps(event)

    # for i in range(1, shop.sales_total_pages + 1):
    # for i in range(1, 10 + 1):
    #     url = shop.get_sales_now_url(i)
    #     payload = {
    #         "name": shop.name,
    #         "id": shop.id,
    #         "url": url
    #     }
    #     payload = json.dumps(payload)
    #     print(payload)
    #     response = boto3.client('lambda').invoke(
    #         FunctionName='buyma-app-dev-hello',
    #         InvocationType='Event',  # Event or RequestResponse
    #         Payload=payload
    #     )

    # return response["Payload"].read().decode("utf-8")


def get_item_list(event, context):
    # {"name": "IMPORT SELECT musee", "id": "841549", "url": "https://www.buyma.com/buyer/841549/sales_2150.html"}

    data = _get_event_data(event)
    s3 = S3(bucket_name=constants.S3_BUCKET)

    try:
        response = requests.get(data["url"])
        soup = BeautifulSoup(response.text, 'html.parser')
        hrefs = [c["href"] for c in soup.select('p.buyeritem_name a')]
        titles = [c.get_text().strip() for c in soup.select('p.buyeritem_name a')]
        order_amounts = [c.get_text().strip().replace("注文数：", "") for c in soup.select('p.buyeritem_name ~p:contains("注文数")')]
        order_dates = [c.get_text().strip().replace("注文日：", "") for c in soup.select('p.buyeritem_name ~p:contains("注文日")')]

        # items = []

        for href, title, order_amount, order_date in zip(hrefs, titles, order_amounts, order_dates):
            # items.append([href, title, order_amount, order_date])
            ptn = r"^/item/(\d+)/$"
            id = re.sub(ptn, r"\1", href)
            csv = ",".join([id, href, title, order_amount, order_date]) + "\n"
            response = s3.upload_item(key="items/%s" % (id,), item=csv)
            # job_log delete
            response = s3.delete_item(key="jobs/shop/%s/%s" % (data["name"], data["url"],))

            # 詳細取得
            payload = {
                "id": id,
                "href": href,
                "title": title,
                "order_amount": order_amount,
                "order_date": order_date
            }
            payload = json.dumps(payload)
            response = boto3.client('lambda').invoke(
                FunctionName='buyma-app-dev-getItemDetail',
                InvocationType='Event',  # Event or RequestResponse
                Payload=payload
            )
    except Exception as e:
        # job_log delete
        print("Exception Occured!!!")
        response = s3.upload_item(key="jobs/shop/%s/%s" % (data["name"], data["url"],), item=e.args[0])


def get_item_detail(event, context):
    #  {"id": "55301234", "href": "/item/55301234/", "title": "DIESEL スイムウェア 水着 海パン SV9U KAXH","order_amount": "1個","order_date": "2020/07/03"}
    try:
        data = _get_event_data(event)
        s3 = S3(bucket_name=constants.S3_BUCKET)

        items = [data["id"], data["href"], data["title"], data["order_amount"], data["order_date"]]

        TOP_URL = "https://www.buyma.com"
        url = TOP_URL + data["href"]

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if soup.select_one(".notfoundSection_txt") is None:
            brands = [c.get_text().strip() for c in soup.select('dt.pt1:contains("ブランド") ~ dd a') if c.get_text().strip() != "商品一覧"]
            brand_1 = brands[0] if len(brands) > 0 else ""
            brand_2 = brands[1] if len(brands) > 1 else ""
            brand_3 = brands[2] if len(brands) > 2 else ""

            categories = [c.get_text().strip() for c in soup.select('dt.pt1:contains("カテゴリ") ~ dd a')]
            category_1 = categories[0] if len(categories) > 0 else ""
            category_2 = categories[1] if len(categories) > 1 else ""
            category_3 = categories[2] if len(categories) > 2 else ""

            price_origin = soup.select_one('p.price_dd strike').get_text().strip() if soup.select_one('p.price_dd strike') is not None else ""

            price = soup.select_one('span.price_txt').get_text().strip() if soup.select_one('span.price_txt') is not None else ""

            colors = [c.get_text().strip() for c in soup.select('span.item_color_name')]

            sizes = [c.get_text().strip() for c in soup.select('table.cse-set__table tr>td:first-child')]

            item_details = [brand_1, brand_2, brand_3, category_1, category_2, category_3, price_origin, price, "@".join(colors), "@".join(sizes)]

            items += item_details

            csv = ",".join(items) + "\n"
            response = s3.upload_item(key="trains/%s" % (data["id"],), item=csv)
            # job_log delete
            response = s3.delete_item(key="jobs/item/%s" % (data["id"]),)
    except Exception as e:
        print("Exception Occured!!!")
        # job_log delete
        response = s3.upload_item(key="jobs/item/%s" % (data["id"],), item=e.args[0])


def get_url(event, context):

    # shop = Shop(constants.shopper_list[0])
    event = {
        # "url": shop.sales_url
        "url": "https://www.buyma.com/item/55541587/"
    }

    data = _get_event_data(event)
    url = data["url"]
    response = requests.get(url)

    if response.status_code == 200:
        get_item_detail({"html_text": response.text}, True)
        # return json.dumps(response)
    else:
        raise Exception


def merge_s3_files():
    s3 = S3(bucket_name=constants.S3_BUCKET)
    keys = s3.list_objects(key="trains/")
    
    print(len(keys))

    with open("/tmp/trains_data.csv", mode="w") as f:
        for key in keys:
            response = s3.get_item(key=key)
            f.write(response["Body"].read().decode("utf-8"))


merge_s3_files()
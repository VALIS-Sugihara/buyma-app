# ①ライブラリのimport
import boto3
# from datetime import datetime


class S3:
    bucket_name = None

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.resource = boto3.resource("s3")

    def upload_item(self, key: str, item: bytes):
        bucket = self.bucket_name  # ⑤バケット名を指定
        # key = 'test_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'  # ⑥オブジェクトのキー情報を指定
        # file_contents = 'Lambda test'  # ⑦ファイルの内容
        # imageBody = base64.b64decode(event['body-json']['base64'])

        obj = self.resource.Object(bucket, key)  # ⑧バケット名とパスを指定
        # obj.put(Body=file_contents)  # ⑨バケットにファイルを出力
        response = obj.put(Body=item)  # ⑨バケットにファイルを出力
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response
        else:
            return False

    def get_item(self, key: str):
        bucket = self.bucket_name

        obj = self.resource.Object(bucket, key)
        response = obj.get()
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response
        else:
            return False

    def download_item(self, key: str, path: str):
        bucket = self.bucket_name

        obj = self.resource.Object(bucket, key)
        response = obj.download_file(path)
        if response is None:
            return True
        else:
            return False

    def delete_item(self, key: str):
        bucket = self.bucket_name

        obj = self.resource.Object(bucket, key)
        response = obj.delete()
        if response is None:
            return True
        else:
            return False

    def list_objects(self, key: str):
        collections = self.resource.Bucket(self.bucket_name).objects.filter(Prefix=key)
        keys = [c.key for c in collections if c.key != key]
        print(keys)
        print(len(keys))
        return keys



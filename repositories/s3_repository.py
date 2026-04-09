import boto3
import json
import logging

from config.settings import settings


logger = logging.getLogger(__name__)

class s3repository:
 def __init__(self, bucket=settings.s3_bucket, key=settings.s3_key):
    self.s3 = boto3.client("s3")
    self.bucket = bucket
    self.key = key

 def get(self) -> dict:
    try:
      data = self.s3.get_object(Bucket=self.bucket, Key=self.key)
      status = json.loads(data["Body"].read().decode("utf-8"))
      logger.info("s3からステータスを読み込み")
    except  self.s3.exceptions.NoSuchKey:
      logger.warning("s3にステータスが存在しません。")
      status = {}
    except Exception as e:
      logger.error("エラー:%s", e)
      status = {}
    return status
 
 def save(self, data: dict) -> None:
    try:
      self.s3.put_object(
      Bucket=self.bucket,
      Key=self.key,
      Body=json.dumps(data, indent=2)
    )
      logger.info("アップロード完了")
    except Exception as e:
      logger.error("アップロード失敗:%s", e)
import os
from dataclasses import dataclass

@dataclass
class Settings:

  ana_url: str = "https://www.ana.co.jp/ja/jp/"

  s3_bucket: str = os.getenv("S3_BUCKET")
  s3_key: str = "ana_sale/monthly_status.json"

  #EMAIL
  SMTP_SERVER: str = "smtp.gmail.com"
  PORT: int = 465
  FROM_EMAIL: str = os.getenv("SENDER_EMAIL")
  APP_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
  TO_EMAIL: str = os.getenv("RECEIVER_EMAIL")

settings = Settings()
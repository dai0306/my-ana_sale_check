import os
import logging
import time
from datetime import datetime
import threading
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
#設定
url = "https://www.ana.co.jp/ja/jp/"

logging.basicConfig(
  filename= "ana_sale/log.txt",
  level= logging.INFO,
  format= "%(asctime)s, %(levelname)s, %(message)s",
  filemode= "a",
  encoding= "utf-8"
  )

#月次状態確認
def monthly_status():
  try:
    with open("ana_sale/monthly_status.json", "r") as file:
      status = json.load(file)

  except FileNotFoundError:
   logging.warning("ファイルが見つかりませんでした。")
   status = {}
   
  return status

#月が変わったらリセット
def reset_monthly_status(status, year, month):
  if status.get("year") != year or status.get("month") != month:
    logging.info(
      "月が変わったためstatusをリセットします(%s-%s -> %s-%s)",
      status.get("year"), 
      status.get("month"),
      year,
      month
     )
    
    status["year"] = year
    status["month"] = month
    status["completed"] = False
    status["last_run"] = None
  return status

#今月は実行済みか
def is_monthly_completed(status, year, month):
  return(
   status.get("year") == year and
   status.get("month") == month and
   status.get("completed")
  )

#月次状態更新
def update_monthly_status(status, year, month, completed, last_run):
  status["year"] = year
  status["month"] = month
  status["completed"] = completed
  status["last_run"] = last_run

  with open("ana_sale/monthly_status.json", "w") as file:
    json.dump(status, file, indent= 4)
    logging.info("月次情報更新")

SMTP_SERVER = "smtp.gmail.com"
PORT = 465
FROM_EMAIL = os.getenv("sender_email")
APP_PASSWORD = os.getenv("sender_password")
TO_EMAIL = os.getenv("receiver_email")

def send_email_with_retry(subject, body, retries=3, base_delay=2):
  msg = MIMEText(body, "plain", "utf-8")
  msg["Subject"] = subject
  msg["From"] = FROM_EMAIL
  msg["To"] = TO_EMAIL
  msg["Date"] = formatdate(localtime=True)

  for count in range(retries):
   
   try:
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as server:
      server.login(FROM_EMAIL, APP_PASSWORD)
      server.set_debuglevel(0)
      server.send_message(msg)
      logging.info("メール送信")
    return True
    
   except smtplib.SMTPRecipientsRefused as e:
     logging.error("宛先拒否:%s", e)
     return False
   
   except Exception as e:
     logging.warning("送信失敗(%d/%d) : %s", count+1, retries, e, exc_info=True)
     time.sleep(base_delay* (2**count))
     return False

options = Options()
options.add_argument("--headless")

status = monthly_status()
now = datetime.now()
current_year = now.year
current_month = now.month

status = reset_monthly_status(status, current_year, current_month)

def ana_sale_check():
 if is_monthly_completed(status, current_year, current_month):
   logging.info("今月実行済み")
   return
 
 logging.info("今月未実行。実行します")
 try:
     driver = webdriver.Edge(options=options)
     driver.get(url)

     elements= WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.asw-heropersonalize-carousel__anchor")))
     logging.info("要素取得開始")

     found = False

     for results in elements:
       try:
        text = results.get_attribute("innerText")
        logging.info("該当要素のテキストを確認")

        if "国内線航空券タイムセール" in text:
          logging.info(f"該当テキストあり:{text}")
          found = True
          break

       except StaleElementReferenceException as e:
         logging.debug("再取得:%s", e)
         continue

       except Exception as e:
         logging.error("例外発生:%s", e)

     if found: 
        thread = threading.Thread(
          target= send_email_with_retry, 
          args=("anaセール情報",f"{text}:https://www.ana.co.jp/ja/jp/")
          )
        thread.start()
        thread.join()
      
        update_monthly_status(status, current_year, current_month, True, now.isoformat())
        logging.info("月次情報更新:%i", now)
     else:
        logging.info("該当テキストなし")

 except Exception as e:
     logging.warning("該当する要素がありません: %s", e, exc_info=True)

 finally:
     driver.quit()
     logging.info("処理終了")
   
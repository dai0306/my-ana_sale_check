import os
import time
from datetime import datetime
import logging

from zoneinfo import ZoneInfo
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.edge.options import Options

from config.settings import settings
from repositories.s3_repository import s3repository
from services.status import reset_monthly_status, is_monthly_completed, update_monthly_status
from services.mail import send_email_with_retry


#設定
url = settings.ana_url
target_text = "国内線航空券タイムセール"
logger = logging.getLogger(__name__)

os.makedirs("ana_sale", exist_ok=True)

def build_driver():
    options = Options()
    options.page_load_strategy = "eager"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Edge(options=options)

def ana_sale_check():
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    current_year = now.year
    current_month = now.month

    if 1 <= now.hour < 8:
      logger.info(f"現在{now.hour}時です。停止時間です。")
      return
    
    s3 = s3repository()
    status = s3.get()
    status = reset_monthly_status(status, current_year, current_month)

    if is_monthly_completed(status, current_year, current_month):
      logger.info("今月実行済み")
      return
 
    logger.info("今月未実行。実行します")
    try:
      driver = build_driver()
      driver.get(url)

      wait = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.asw-heropersonalize-carousel__anchor")))
      logger.info("要素取得開始")
      element = driver.find_element(By.CSS_SELECTOR, "a.asw-heropersonalize-carousel__anchor")
      
      if element:
        try:
         driver.get(element)
         wait = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.main-visual img")))
         img = driver.find_element(By.CSS_SELECTOR, "div.main-visual img")
         text = img.get_attribute("alt")

         if target_text in text:
           thread = threading.Thread(
            target= send_email_with_retry, 
            args=("anaセール情報",f"{text}:https://www.ana.co.jp/ja/jp/")
          )
           thread.start()
           thread.join()

           update_monthly_status(status, current_year, current_month, True, now.isoformat())
           logger.info("月次情報更新:%s", now)

           
        except StaleElementReferenceException as e:
          logger.warning("見つかりません:%s", e)

        except TimeoutException as e:
          logger.error("timeout:%s", e)

        except Exception as e:
          logger.error("例外発生:%s", e)

      else:
        logger.info("該当テキストなし")

    except StaleElementReferenceException as e:
      logger.warning("見つかりません:%s", e)

    except TimeoutException as e:
      logger.error("timeout:%s", e)

    except Exception as e:
      logger.warning("該当する要素がありません: %s", e, exc_info=True)

    finally:
      driver.quit()
      logger.info("処理終了")



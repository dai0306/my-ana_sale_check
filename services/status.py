
import logging

from repositories.s3_repository import s3repository

logger = logging.getLogger(__name__)

s3 = s3repository()

def reset_monthly_status(status, year, month):
  if status.get("year") != year or status.get("month") != month:
    logger.info(
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

    s3.save(status)

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

  s3.save(status)
import logging

def configure_logging():
  
  root_logger = logging.getLogger()
  
  formatter = logging.Formatter("%(asctime)s, %(levelname)s, %(funcName)s,[%(lineno)d], %(message)s")

  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  console_handler.setFormatter(formatter)

  file_handler = logging.FileHandler("ana_sale/log.txt", encoding="utf-8", mode="a")
  file_handler.setLevel(logging.INFO)
  file_handler.setFormatter(formatter)

  root_logger.setLevel(logging.INFO)
  root_logger.addHandler(console_handler)
  root_logger.addHandler(file_handler)


  
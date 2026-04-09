from ana_sale.production_operation import ana_sale_check
from utils.log_config import configure_logging

if __name__ == "__main__":
  configure_logging()
  ana_sale_check()
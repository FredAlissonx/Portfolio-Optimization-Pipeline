from dotenv import load_dotenv
from utils.logging_setup import LoggingSetup
import requests

load_dotenv()

session = requests.session()

bronze_logger = LoggingSetup.get_bronze_logger()
silver_logger = LoggingSetup.get_silver_logger()
gold_logger = LoggingSetup.get_gold_logger()
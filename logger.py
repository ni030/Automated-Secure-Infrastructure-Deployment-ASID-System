import logging
import os

# 确保 logs folder 存在
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/deploy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
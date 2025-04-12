# logger_config.py
import logging
from datetime import datetime

def setup_logger(log_file: str = "app.log"):
    # Generate a timestamped log file name
    timestamp = datetime.now().strftime("%d%m%Y")
    log_file = f"{log_file.rstrip('.log')}-{timestamp}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=log_file,
        filemode="a"  # append to file
    )

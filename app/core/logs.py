import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
console_output_handler = logging.StreamHandler()
logger.addHandler(console_output_handler)
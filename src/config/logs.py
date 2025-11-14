import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("weaviate").setLevel(logging.WARNING)
logger = logging.getLogger("rag")
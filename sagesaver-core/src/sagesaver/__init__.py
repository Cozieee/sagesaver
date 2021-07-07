import logging
from .server import Server

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

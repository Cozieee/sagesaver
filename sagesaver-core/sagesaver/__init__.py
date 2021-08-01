import logging
from pathlib import Path

PACKAGEDIR = Path(__file__).parent.absolute()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

import logging

from deps_workflow_manager.settings import Settings

logging.basicConfig(
    level=Settings().logger_level.upper(),
    format="[%(asctime)s] [%(name)s: %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
)
logging.getLogger("pika").setLevel(logging.CRITICAL)

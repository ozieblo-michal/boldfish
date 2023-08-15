import logging


def log_entities(entities: str) -> None:
    logger = logging.getLogger("configure_logger")
    entities_list = entities.split(", ")
    entities_list.sort(key=str.lower)
    entities_sorted = ", ".join(entities_list)
    logger.info(f"Processed entities in this session: {entities_sorted}")

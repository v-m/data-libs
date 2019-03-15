from logger import get_logger

# import logger.some_shit

log = get_logger()
log.debug("Debug voerfew32_unique_t23miv")
log.info("Info voerfew32_unique_t23miv")
log.warning("Warn voerfew32_unique_t23miv")
log.error("Error voerfew32_unique_t23miv")
log.critical("Critical message voerfew32_unique_t23miv")

# time.sleep(1)
try:
    0 / 0
except Exception as e:
    log.exception(e)

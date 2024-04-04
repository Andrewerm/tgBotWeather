import betterlogging as logging

from betterlogging import ColorizedFormatter
from pythonjsonlogger import jsonlogger
import betterlogging as bl

from tgbot.config import load_config

config = load_config()


class YcLoggingFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(YcLoggingFormatter, self).add_fields(log_record, record, message_dict)
        log_record['logger'] = record.name
        log_record['level'] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")


def setup_custom_logger(name):
    logHandler = logging.StreamHandler()
    if config.misc.app_env == 'yandex':
        logger = logging.getLogger(name)
        logHandler.setFormatter(YcLoggingFormatter(fmt='%(message)s %(level)s %(logger)s'))
    else:
        logger = logging.get_colorized_logger(name)
        logHandler.setFormatter(logging.ColorizedFormatter())
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(logHandler)

    return logger

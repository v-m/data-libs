from typing import Optional, Union

import logging
import logging.config

from os import environ, _Environ
from pathlib import Path
from pkgutil import get_data

import yaml

from .formatters import color_formatter
from .formatters import stackdriver_formatter

DEFAULTS = {
    "LOG_FILE_LOCATION": "/tmp/python-log.log",
    "LOG_ROTATING_INTERVAL": "h",
    # "APP_NAME": "Python application",
    "LOG_LEVEL_CONSOLE": "INFO",
    "LOG_LEVEL_FILE": "DEBUG",
    "LOG_SLACK_USER": "Logger",
    "DEFAULT_SLACK_CHANNEL": "NOT_SET",
    "LOG_SLACK_TOKEN": "NOT_SET",  # This should be overriden, otherwise message will not be sent
}

STACKDRIVER_LOGGING_ENABLE_VAR = "STACKDRIVER_LOGGING_ENABLE"


LOGGING_CONFIG_LOCATION = environ.get("LOG_CONFIG_PATH")


def _load_logging_config_(params):

    params.update({k: v for k, v in DEFAULTS.items() if k not in params})

    if LOGGING_CONFIG_LOCATION:
        with open(LOGGING_CONFIG_LOCATION) as f:
            config_str = f.read()
    else:
        config_data = get_data("revlibs.logger", "resources/logging.yaml")
        if config_data:
            config_str = config_data.decode("utf-8")
        else:
            raise Exception("Coould not find default logging.yaml")
    return yaml.load(config_str.format(**params), Loader=yaml.Loader)


def get_logger(name=None, params: Union[dict, _Environ] = None):
    """
    Initialise the logger using the logging.yaml template
    Use environ() where no parameters are specified
    """
    if not params:
        params = environ

    config = _load_logging_config_(params)
    logging.config.dictConfig(config)
    log = logging.getLogger(name)

    if params.get(STACKDRIVER_LOGGING_ENABLE_VAR, "FALSE").upper() == "TRUE":
        log.info("STACKDRIVER enabled")
        stackdriver_formatter.add_stack_driver_support(log)

    return log

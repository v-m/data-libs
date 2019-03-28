""" Handles the connection config."""
import os
import logging
from pathlib import Path

from revlibs.dicts import DictLoader


_DEFAULT_DIRECTORY = Path.home() / ".revconnect/"
_ENV_VAR_FOR_FILE = "REVLIB_CONNECTIONS"


class Config:
    """Connection config."""

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def __repr__(self):
        """ Print the config. Will not print secrets if they
        are not contained in the connection file.
        """
        return repr(self.config)

    def __contains__(self, item):
        """ Determine if config has an attr."""
        return item in self.config.keys()

    def __getattr__(self, key):
        """ Get attr from environment, if not set return default."""
        if key in self.config:
            result = self.config[key]
            if result.startswith("_env"):
                var_split = result.split(":", 2)
                var_name = var_split[1]
                var_default = "" if len(var_split) < 3 else var_split[2]
                result = os.environ.get(var_name, var_default)
            return result
        raise NameError(f"Database flavour requires '{key}'.")


def connections_settings():
    """ Retrieve connections from specified yaml."""
    directory = os.environ.get(_ENV_VAR_FOR_FILE, _DEFAULT_DIRECTORY)
    loader = DictLoader.from_path(directory)
    return loader


def load(database):
    """ Load the database connection configuration."""
    connections = connections_settings()

    for item in connections.items:
        if database in item:
            db_config = item[database]
            break
    else:
        logging.error(f"No config for db called: '%s'.", database)
        return None

    cfg = Config(database, db_config)
    if "disabled" in cfg and cfg.disabled is True:
        return None
    return cfg

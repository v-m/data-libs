""" Handles the connection config."""
import os
import logging
from pathlib import Path

import yaml


log = logging.getLogger(__name__)


_DEFAULT_FILE = Path.home() / ".revconnect"
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


def connections_file():
    """ Retrieve connections from specified yaml."""
    revconnect_path = os.environ.get(_ENV_VAR_FOR_FILE, _DEFAULT_FILE)
    with open(Path(revconnect_path)) as file:
        connections = yaml.load(file)
    return connections


def db_names():
    """ Retrieve names of connections."""
    conn = connections_file()
    return list(conn.keys())


def load(database):
    """ Load the database connection configuration."""
    connections = connections_file()

    try:
        db_config = connections[database]
    except KeyError as err:
        log.exception(err, f"No config for db called: '{database}'.")
        raise

    return Config(database, db_config)

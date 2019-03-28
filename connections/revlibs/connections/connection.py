""" Standard connection interface."""
import logging
from contextlib import contextmanager

import psycopg2

from revlibs.connections import config

log = logging.getLogger(__name__)


class ConnectExasol:
    pass


class ConnectPostgres:
    """ Bridges the standard method of connecting to a database and postgres."""

    def __init__(self, cfg):
        self.name = cfg.name
        self.dsn = cfg.dsn
        self.config = cfg

    def _parse_dsn(self, data_source_name):
        """ We need to parse the standard dsn string into
        an acceptable format for postgres.

        'localhost:8888' -> 'host=localhost port=8888'
        """
        dsns = data_source_name.split(",")
        for dsn in dsns:
            host, port = dsn.split(":")
            yield f"host={host} port={port}"

    def connect(self):
        """ Attempt to connect to postgres."""
        dbname = self.config.dbname if ("dbname" in self.config) else None
        for data_source_name in self._parse_dsn(self.dsn):
            try:
                self.connection = psycopg2.connect(
                    data_source_name,
                    user=self.config.user,
                    password=self.config.password,
                    dbname=dbname,
                )
                break
            except psycopg2.OperationalError as err:
                log.exception(err)
                continue
        return self.connection

    def close(self):
        """ Close the connection."""
        self.connection.close()


_CONNECTORS = {"exasol": ConnectExasol, "postgres": ConnectPostgres}


@contextmanager
def get(name):
    """ Grab a connection."""
    cfg = config.load(name)
    obj = _CONNECTORS[cfg.flavour]
    connector = obj(cfg)
    yield connector.connect()
    connector.close()

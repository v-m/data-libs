""" Standard connection interface."""
import logging
from contextlib import contextmanager

import psycopg2
import pyexasol

from revlibs.connections import config

log = logging.getLogger(__name__)


class ConnectExasol:
    """ Bridge method of connecting and exasol."""

    def __init__(self, cfg):
        self.name = cfg.name
        #: We follow the pyexasol convention of dsn.
        self.dsn = cfg.dsn
        self.config = cfg

    def connect(self):
        """ Attempt to connect to exasol."""
        schema = self.config.schema if ("schema" in self.config) else None
        params = {"schema": schema, "compression": True}
        try:
            self.connection = pyexasol.connect(
                dsn=self.dsn,
                user=self.config.user,
                password=self.config.password,
                fetch_dict=True,
                **params,
            )
        except pyexasol.exceptions.ExaError as err:
            log.exception(err)
        return self.connection


class ConnectPostgres:
    """ Bridges method of connecting and postgres."""

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
    if connector:
        yield connector.connect()
        connector.close()
    else:
        yield None

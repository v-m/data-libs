from abc import abstractmethod
import os
import psycopg2
import pyexasol
from revlibs.logger import get_logger

from .connection_model import Connection, DBConnection
from .registry import register_connector
from .utils import as_list, extend

log = get_logger()


"""
This is a library of functions for returning connections to all kinds of dbms
The `register_connector` decorator is here just to 
"""


@register_connector("postgres")
def posgres_connect(db_conn: DBConnection):

    """
    Connect to a PostgresSQL database, using the config object provided
    :return: psycopg2 cursor object
    """
    conn_tpl = "host='{host}' dbname='{db}' user='{user}' password='{passw}' port='{port}'"
    hosts = as_list(db_conn.hosts)
    password = os.getenv(db_conn.password, "")
    ports = extend(db_conn.ports, len(hosts))
    conn_string = conn_tpl.format(
        host=",".join(db_conn.hosts).format(**os.environ),
        db=db_conn.schema.format(**os.environ),
        user=db_conn.user.format(**os.environ),
        passw=password,
        port=",".join(str(port).format(**os.environ) for port in ports),
    )
    try:
        # get a connection, if a connect cannot be made an exception will be raised here
        postgres_conn = psycopg2.connect(conn_string)
        # postgres_conn.set_session(readonly=True, autocommit=True)
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        return postgres_conn

    except psycopg2.OperationalError as e:
        log.error(
            "Could not connect to database. Connection string: %s",
            conn_string.replace(password, "****"),
        )
        log.exception(e)
    return None


@register_connector("exasol")
def exasol_connect(db_conn: DBConnection):
    password = os.environ.get(db_conn.password, "")
    hosts = ",".join(db_conn.hosts).format(**os.environ)
    ports = extend(db_conn.ports, len(hosts))
    dsn = ",".join(f"{k}:{v}" for (k, v) in zip(db_conn.hosts, ports)).format(**os.environ)
    params = {"schema": db_conn.schema, "compression": True}
    params.update(db_conn.params)
    try:
        connection: pyexasol.ExaConnection = pyexasol.connect(
            dsn=dsn,
            user=db_conn.user.format(**os.environ),
            password=password,
            fetch_dict=True,
            **params,
        )
        return connection
    except Exception as e:
        log.error(
            "Could not connect to Exasol database. Connection string: %s",
            dsn.replace(password, "****"),
        )

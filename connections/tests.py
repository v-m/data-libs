import os
import pytest
import psycopg2
import pyexasol
from revlibs.connections import get_connection_by_name


class ConnectionMock:
    def __init__(self, *x, **y):
        self.input = x
        self.vars = y

    def close(self):
        pass


def test_simple_postgres(monkeypatch):
    monkeypatch.setattr(psycopg2, "connect", lambda x: ConnectionMock(x))
    with get_connection_by_name("postgres_simple") as connection:
        expected_connection_str = "host='{host}' dbname='{db}' user='{user}' password='{passw}' port='{port}'".format(
            host="127.0.0.1", db="s", user="test", passw=os.environ.get("TEST_PASS"), port=5436
        )
        assert connection.input[0] == expected_connection_str


def test_multi_server_postgres(monkeypatch):
    monkeypatch.setattr(psycopg2, "connect", lambda x: ConnectionMock(x))
    with get_connection_by_name("postgres_multi_server") as connection:
        expected_connection_str = "host='{host1},{host2}' dbname='{db}' user='{user}' password='{passw}' port='{port},{port}'".format(
            host1="127.0.0.1",
            host2="127.0.0.2",
            db="s",
            user="test",
            passw=os.environ.get("TEST_PASS"),
            port=5436,
        )
        assert connection.input[0] == expected_connection_str


def test_multi_server_exasol(monkeypatch):
    monkeypatch.setattr(pyexasol, "connect", lambda **x: ConnectionMock(**x))
    with get_connection_by_name("exasol_multi_server") as connection:
        expected_connection_dsn = "{host1}:{port1},{host2}:{port2}".format(
            host1="127.0.0.1", host2="127.0.0.1", port1=5436, port2=5437
        )
        assert connection.vars["dsn"] == expected_connection_dsn
        assert connection.vars["user"] == "test"
        assert connection.vars["schema"] == "s"


def test_disabled_connection():
    with pytest.raises(KeyError):
        with get_connection_by_name("postgres_disabled") as connection:
            assert not connection, "Disabled connections are not handled"


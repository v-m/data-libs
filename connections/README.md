# Revlibs Connections

Get connected instantly to a predefined set of databases, regardless of their type and nature.

## Install

```
pip install revlibs-connections
```

## Usage

```python

from revlibs import connections

with connections.get("revdata") as conn:
    conn.execute(query)
```

### Connections

This connection library will use the connections specified in the yaml `~/.revconnect`.
If you would like to specify a different file. You may use the `"REVLIB_CONNECTIONS"`
environment variable.

#### E.g:

```
export REVLIB_CONNECTIONS=<path_to_different_file>
```

#### An example of this file is provided below

```yaml
# Postgres Example
sandboxdb:
    flavour: postgres
    # We can specify multiple <host:port> combinations.
    # To simplfy this you may also provide
    # '127.0.0.1..3:8888' which will attempt sequential
    # connectiosn from '.1' -> '.3'
    dsn: 127.0.0.1:8888,127.0.0.1:8889
    user: postgres
    password: _env:SANDBOXDB_PASSWORD
    dbname: countries

# Exasol example
bigdb:
    flavour: exasol
    dsn: _env:BIG_DB_DSN
    user: default_user
    password: _env:BIGDB_PASSWORD
    schema: events
```

#### Note

Ensure you have no collision with environment variables by prefixing
you environment connection parameters with your connection name. E.g.
the env var for the sandboxdb will be called `SANDBOXDB_PASSWORD`.

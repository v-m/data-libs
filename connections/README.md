<h1 align="center">
    Revlibs Connections
</h1>

<h4 align="center">
    Get connected instantly to a predefined set of databases, regardless of their type and nature.
</h4>

## Install

```
pip install revlibs-connections
```

## Usage

```python

from revlibs import connections

with connections.get("sandboxdb") as conn:
    conn.execute(query)
```

### Connections

This connection library will use the 'yaml/json' connections specified in the directory `~/.revconnect/`.
If you would like to specify a different path.

```
- .revconnect/
    ├ connections.yaml
    └ connections.json
```

#### E.g:

You may change the `"REVLIB_CONNECTIONS"`
environment variable.

```
export REVLIB_CONNECTIONS=<path_to_different_file>
```

#### An example of this file is provided below

We can have multiple connections in a single file.

*Note:* We have enforced taking the `password` from the environment.

```yaml
# Postgres Example
- name: sandboxdb
  flavour: postgres
  # We can specify multiple <host:port> combinations.
  # To simplfy this you may also provide
  # '127.0.0.1..3:8888' which will attempt sequential
  # connectiosn from '.1' -> '.3'
  dsn: 127.0.0.1:8888,127.0.0.1:8889
  user: postgres
  # Specifying the environment variable
  password: _env:SANDBOXDB_PASSWORD
  dbname: countries

# Exasol example
- name: bigdb
  flavour: exasol
  dsn: _env:BIG_DB_DSN
  user: default_user
  password: _env:BIGDB_PASSWORD
  schema: events
```

Ensure you have no collision with environment variables by prefixing
your environment connection parameters with your connection name. E.g.
the env var for the sandboxdb will be called `SANDBOXDB_PASSWORD`.

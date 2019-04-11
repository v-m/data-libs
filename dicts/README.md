# Dicts

An API for manipulating `Dicts` where `Dicts = List[dict]`

`Dicts` assumes you have a set of dictionaries which share a structure, such as a `jsonschema`.
This library aims to simplify common operations that might need to be performed on lists of dictionaries.

`Dicts` doesn't care whether your source is. You can load from

 - A `json` or `yaml` file
 - A directory
 - An object of `List[dict]`

## Usage

Say we have a configuration files `connections.yaml`

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

---

# Exasol example
- name: bigdb
  flavour: exasol
  dsn: _env:BIG_DB_DSN
  user: default_user
  password: _env:BIGDB_PASSWORD
  schema: events
```

Note that this is a contrived example as the implicit `jsonschema` is so simple. Then, with `revlibs.dicts` we can load the config

```python
import os

from pathlib import Path
from revlibs.dicts import Dicts, PATH_KEY

HOME = os.environ['APP_DIR']
path = Path() / HOME / "config/connections.yaml"

loader = Dicts.from_path(path)
list(loader.items)
```

would output

```python
[{'__PATH__': '$APP_DIR/config/connections.yaml',
  'dbname': 'countries',
  'dsn': '127.0.0.1:8888,127.0.0.1:8889',
  'flavour': 'postgres',
  'name': 'sandboxdb',
  'password': '_env:SANDBOXDB_PASSWORD',
  'user': 'postgres'},
 {'__PATH__': '$APP_DIR/config/connections.yaml',
  'dsn': '_env:BIG_DB_DSN',
  'flavour': 'exasol',
  'name': 'bigdb',
  'password': '_env:BIGDB_PASSWORD',
  'schema': 'events',
  'user': 'default_user'}]
```

The loader can be configured to skip and log errors instead of raising.

```python
loader = Dicts.from_path(path, skip_errors=True)
```

The loader can be forced to load disabled entries. Disabled entries are specified in the config file via the `disabled_key` argument.

```python
loader = Dicts.from_path(path, 
    disabled_key="disable",
    load_disabled_entries=True)
```

You can key the items by some function 

```python
loader = Dicts.from_dicts(
    [
        {"animal": "cat", "size": "100"},
        {"animal": "dog", "size": "100"},
        {"animal": "rat", "size": "1"}
    ]
)

loader.filter(lambda d: d["animal"] == "rat").items
```

```
# You can transform the values from dict to any other object
loader.group_by_key(transformator=Table.__init__)

# By default, the key 'name' is used. You can override it and specify either or key even an expression
loader.group_by_key(key='id')
loader.group_by_key(key=lambda d: d['id']+d['name'])

# If there are items with duplicate keys, it will throw an exception. However, we can override it
# to only write a warning and not raise the exception:
loader.group_by_key(key='id', allow_duplicates=True)


# To group loaded items by file name, use group_by_file. This will group by __PATH__
# and have a list of items for each:
loader.group_by_file()
# You can also specify the transformator
loader.group_by_file(transformator=Table.__init__)
```

# Dicts

A library for loading json/yaml files from directories and single files.

## Usage

```python
from pathlib import Path
from dicts import DictLoader, PATH_KEY
p = Path("revolut-datascience/infra/helios/config/tables")
p = Path("../../revolut-datascience/infra/helios/config/tables")

# You can also load a single file
p = Path("revolut-datascience/infra/helios/config/tables/users.yaml")

# Json files are also supported
p = Path("revolut-datascience/infra/helios/config/tables/users.json")

# Instantiate the loader
loader = DictLoader.from_path(p)

# By default, if yaml/json files are invalid, it will just warn and skip them.
# Alternatively, you ask the loader to fail in such case
loader = DictLoader.from_path(p, skip_errors=True)

# By default we skip yaml/json files which are disabled by having `disable: True`. We can override this
loader = DictLoader.from_path(p, load_disabled_entries=True)

# We can even override the disabled key
loader = DictLoader.from_path(p, disabled_key='active', load_disabled_entries=True)

# To access items, just access items :)
# Each resulting dict also has an extra key "__PATH__", indicating the original file location
loader.items

# If your file is guaranteed to have only one dict, you need to get it out of the list:
loader.items[0]

# This will give you a dict of all the dicts found under a given path
loader.group_by_key()

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

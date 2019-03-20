# Revlibs Connections

Get connected instantly to a predefined set of databases, regardless of their type and nature.

```yaml
name: my_db
type: postgres
params:
  hosts: [127.0.0.1, "{FAILOVER_HOST}"] # you can also use environment variables here
  ports: [5432, "{FAILOVER_PORT}"] # and here as well
  user: test
  password: SECRET_PASSWORD # this must be an environment variable name, not actual password
  schema: my_stuff
```

```python
with get_connection_by_name("my_db") as connection:
        connection.execute("select 1")
        )
```

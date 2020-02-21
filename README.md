[![Build Status](https://travis-ci.com/adrenalin/config.svg?branch=master)](https://travis-ci.com/adrenalin/config)

# 1 Configuration

There are three levels that can be used to override configuration settings:

1. [local configuration file](#local-configuration-files)
2. [environment variables](#environment-variables)
3. [AWS SecretsManager](#aws-secretsmanager)

## <a name="local-configuration-files"></a> 1.1 Local configuration file

It is possible to override database string in file `./config/local.yml`. Local
configuration options override per key the ones defined in `./config/defaults.yml`
which are used when there are no overrides.

```
db:
  name: 'example'
  username: 'database_admin_username'
  password: 'database_admin_password'
```

## <a name="environment-variables"></a> 1.2 Environment variables

It is possible override any default and local configuration by using environment
variables. Environment variables follow the same naming scheme as configuration
paths, but in uppercase and separated by underscore (`_`).

E.g. configuration path `db.username` can be overridden with `DB_USERNAME` and
correspondingly `server.session.engine` with `SERVER_SESSION_ENGINE`.

If `DB_CONNECTION_STRING` is present it is used fully. Otherwise a combination of
`DB_USERNAME`, `DB_PASSWORD`, `DB_HOST` and `DB_NAME` will be used.

Environment variables are used on the command line in the following manner:

```
DB_USERNAME=example DB_PASSWORD=randompassword DB_NAME=example python3 application.py
DB_CONNECTION_STRING=postgresql:///example:password@localhost/example python3 application.py
```

Environment variables are especially for production use, for development it is
recommended to create a local configuration file as described above.

There are three case insensitive magic environment variables that are type cast:

- `false` is cast `False`
- `true` is cast as `True`
- `null` and `none` are cast as `None`

This leads into easier true/false evaluations in the code. For example this will
disable AWS SecretsManager when running the application:

`AWS_SECRETSMANAGER_ENABLED=false python3 application.py`

## <a name="aws-secretsmanager"></a> 1.3 AWS SecretsManager

The final layer of configurability is on2
[AWS SecretsManager](https://eu-north-1.console.aws.amazon.com/secretsmanager/home?region=eu-north-1).

### 2.3.1 Normal values

Each configuration key can be overridden by the string representation of the
configuration path. E.g. configuration option

```
db:
  connection_string: 'postgresql://postgres@localhost/example'
```

can be overridden with AWS SecretsManager secret key `db.connection_string`


### 1.3.2 Prefixed values

Since it is expected that as the system grows there might be conflicts in the
naming. It is possible to use prefixed strings to avoid inter application
conflicts. Prefix is defined as `aws.secretsmanager.prefix`, which is
prepended to the configuration key read from AWS SecretsManager, i.e.
system with secretsmanager prefix `dev` will read `dev@db.connection_string`
as `db.connection_string` and skip any secret that has a prefix that does not
match. Secrets without a prefix are included.

Prefixed values have priority over values without a prefix, i.e.
`dev@db.connection_string` is used instead of `db.connection_string` when both
are present.

### 1.3.3 Skipping unprefixed values

To fetch strictly prefixed values to keep the configuration more clean, set the
flag for `aws.secretsmanager.skip_unprefixed` to `True`

```
config.set('aws.secretsmanager.enabled', True)
config.set('aws.secretsmanager.prefix', 'my-prefix')
config.set('aws.secretsmanager.skip_unprefixed', True)
config.load_secrets()
```

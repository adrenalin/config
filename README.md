[![Build Status](https://travis-ci.com/adrenalin/config.svg?branch=master)](https://travis-ci.com/adrenalin/config) [![Coverage Status](https://coveralls.io/repos/github/adrenalin/config/badge.svg)](https://coveralls.io/github/adrenalin/config)

# 1 Configuration

There are four levels that can be used to override configuration settings:

1. [local configuration file](#local-configuration-files)
2. [environment variables](#environment-variables)
3. [AWS SecretsManager](#aws-secretsmanager)
4. [Azure Key Vaule](#azure-keyvault)



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

An optional layer of configurability is on
[AWS SecretsManager](https://eu-north-1.console.aws.amazon.com/secretsmanager/home?region=eu-north-1).


### 1.3.1 Normal values

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



## <a name="azure-keyvault"></a> 1.4 Azure Key Vault

Configuration keys can be stored also to Microsoft Azure's Key Vault. You will
need to provide the following configuration options

Service principal with secret:

```
azure:
  # ID of the service principal's tenant. Also called its 'directory' ID.
  tenant_id: ''

  # the service principal's client ID
  client_id: ''

  # one of the service principal's client secrets
  client_secret: ''
```

Service principal with certificate:

```
azure:
  # ID of the service principal's tenant. Also called its 'directory' ID.
  tenant_id: ''

  # the service principal's client ID
  client_id: ''

  # Path to a PEM-encoded certificate file including the private key. The
  # certificate must not be password-protected
  client_certificate_path: ''
```

User with username and password:

```
azure:
  # the service principal's client ID
  client_id: ''

  # a username (usually an email address)
  username: ''

  # that user's password
  password: ''

  # (optional) ID of the service principal's tenant. Also called its 'directory'
  # ID. If not provided, defaults to the 'organizations' tenant, which supports
  # only Azure Active Directory work or school accounts.
  tenant_id: ''
```

Configuration may be either loaded to the configuration prior to loading the
key vault with `config.load_secrets()` or set as environment variables
(uppercase, separated with underscore, e.g. `AZURE_TENANT_ID` or
`AZURE_CLIENT_CERTIFICATE_PATH`)


### 1.4.1 Normal values

Each configuration key can be overridden by the string representation of the
configuration path. E.g. configuration option

```
db:
  connection_string: 'postgresql://postgres@localhost/example'
```

can be overridden with Azure Key Vault key `db.connection_string`


### 1.4.2 Prefixed values

Since it is expected that as the system grows there might be conflicts in the
naming. It is possible to use prefixed strings to avoid inter application
conflicts. Prefix is defined as `azure.keyvault.prefix`, which is
prepended to the configuration key read from Azure Key Vault, i.e.
system with key prefix `dev` will read `dev@db.connection_string`
as `db.connection_string` and skip any secret that has a prefix that does not
match. Values without a prefix are included.

Prefixed values have priority over values without a prefix, i.e.
`dev@db.connection_string` is used instead of `db.connection_string` when both
are present.


### 1.4.3 Skipping unprefixed values

To fetch strictly prefixed values to keep the configuration more clean, set the
flag for `azure.keyvault.skip_unprefixed` to `True`

```
config.set('azure.keyvault.enabled', True)
config.set('azure.keyvault.prefix', 'my-prefix')
config.set('azure.keyvault.skip_unprefixed', True)
config.load_secrets()
```

### 1.4.4 Secret storage format in Azure Key Vault

Since Azure Key Vault allows naming secrets only with alphabets and scores
(a-z, -) the separators are marked in the following order

- prefix uses `---` (AWS Secrets Manager equivalent of `@`)
- dot uses `--` (configuration key path equivalent of `.`)
- the remaining sores are translated as underscore `_`

E.g. secret name `test-prefix---db--connection-string` populates the
configuration path `db.connection_string` when `azure.keyvault.prefix` matches
`test-prefix`

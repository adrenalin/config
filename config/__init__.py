"""
Configuration is a helper class for loading and overriding configuration with
ease. Basic usage::

    import os
    from lib import Config

    config = Config()
    config.load_config(os.path.join('config', 'defaults.yml'))
    config.load_config(os.path.join('config', 'local.yml'), graceful=True)
    config.load_secrets()

Configuration is stored in the load order, latest overwriting earlier values.
All values are merged to the previous.

Configuration files
-------------------

Configuration files are stored as YAML. An example configuration::

    db:
      name: 'aistest'
      username: 'ais_database_admin_username'
      password: 'ais_database_admin_password'


Environment variables
---------------------

It is possible override any default and local configuration by using environment
variables. Environment variables follow the same naming scheme as configuration
paths, but in uppercase and separated by underscore (`_`).

E.g. configuration path `db.username` can be overridden with `DB_USERNAME` and
correspondingly `server.session.engine` with `SERVER_SESSION_ENGINE`.

If `DB_CONNECTION_STRING` is present it is used fully. Otherwise a combination of
`DB_USERNAME`, `DB_PASSWORD`, `DB_HOST` and `DB_NAME` will be used.

Environment variables are used on the command line in the following manner::

    DB_USERNAME=aistest DB_PASSWORD=randompassword DB_NAME=ais pytest
    DB_CONNECTION_STRING=postgresql:///aistest alembic upgrade base

Environment variables are especially for production use, for development it is
recommended to create a local configuration file as described above.

There are three case insensitive magic environment variables that are typecasted:

- `false` is casted as `False`
- `true` is casted as `True`
- `null` and `none` are casted as `None`

This leads into easier true/false evaluations in the code. For example this will
disable AWS SecretsManager when running the application::

    AWS_SECRETSMANAGER_ENABLED=false python3 application.py

AWS SecretsManager
------------------

The final layer of configurability is on AWS

**Normal values**

Each configuration key can be overridden by the string representation of the
configuration path. E.g. configuration option::

    db:
      connection_string: 'postgresql://postgres@localhost/ais'

can be overridden with AWS SecretsManager secret key `db.connection_string`


**Namespaced values**

Since it is expected that as the system grows there might be conflicts in the
naming. It is possible to use namespaced strings to avoid inter application
conflicts. Namespace is defined in `aws.secretsmanager.prefix`, which is
prepended to the configuration key read from AWS SecretsManager, i.e.
system with secretsmanager prefix `ais-dev` will read `ais-dev@db.connection_string`
as `db.connection_string` and skip any prefixed secret that does not match.

**Full configuration**

If the configuration key is "config" it is treated as a full configuration
object. Full configuration object can be stored either as JSON or its derivative
YAML.

**Supported formats**

Configuration values can be JSON, YAML or plain strings. Internal heuristics
try to typecast the value in the beforementioned orner.

@author Arttu Manninen <arttu@kaktus.cc>
"""
import os
import json
import re
import sys
import yaml
from config.boto3 import Boto3
from config.merge import merge

boto3 = Boto3()

class Config():
    """ Configuration manager """
    Config = None
    def __init__(self):
        # Load the project configuration immediately
        self._config = {}
        self._secrets = {}

    def set(self, config_key_path: 'Union(str, list)' = '', value: 'mixed' = None) -> 'self':
        """ Set configuration key """
        separator = '.'

        if not config_key_path:
            assert isinstance(value, dict)
            self._config = merge(self._config, value)
            return self

        if isinstance(config_key_path, str):
            config_key_path = config_key_path.split(separator)

        if isinstance(config_key_path, tuple):
            config_key_path = list(config_key_path)

        assert isinstance(config_key_path, list)

        cfg = self._config
        last_key = config_key_path.pop()

        for _i, key in enumerate(config_key_path):
            cfg = cfg.setdefault(key, {})

        cfg[last_key] = value
        return self

    def get(self, key: 'Union(str, list)' = '', **kwargs) -> 'mixed':
        """ Get configuration key """
        return self.get_config_key(
            key,
            configuration=self._config,
            **kwargs
        )

    @staticmethod
    def _parse_secret_value(value: str):
        """ Parse secret value """
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError:
            pass

        try:
            return yaml.load(value, Loader=yaml.Loader)
        except yaml.scanner.ScannerError:
            return value

    def load_secrets(self) -> 'self':
        """ Load AWS SecretManager secrets to the configuration """
        if not self.get('aws.secretsmanager.enabled'):
            return self

        prefix = self.get('aws.secretsmanager.prefix', default='')
        client = boto3.client('secretsmanager')
        paginator = client.get_paginator('list_secrets')
        secrets = []

        for page in paginator.paginate():
            for _i, secret_metadata in enumerate(page['SecretList']):
                secrets.append(secret_metadata)

        def sort_secrets(secret):
            """ Sort secrets """
            if '@' in secret['Name']:
                return 1
            return 0

        secrets.sort(key=sort_secrets)

        for secret_metadata in secrets:
            name = secret_metadata['Name']
            key = name

            if prefix and re.search('@', key):
                if name.find(prefix + '@') != 0:
                    continue
                key = name[len(prefix) + 1:]

            stored_secret = client.get_secret_value(SecretId=name)
            stored_value = self._parse_secret_value(stored_secret['SecretString'])

            # Special case: when the name of the secret is "config" it is handled
            # as a full set of configuration instead of a subset
            if key == 'config':
                self.set(None, stored_value)
                break

            self.set(key, stored_value)

        return self

    def load_configuration(self, file_path: str, graceful: bool = False) -> 'self':
        """ Load configuration """
        if not os.path.exists(file_path):
            if not graceful:
                raise FileNotFoundError('File %s not found' % (file_path))
            return self

        with open(file_path) as ymlfile:
            values = yaml.load(ymlfile, Loader=yaml.Loader) or {}
            self._config = merge(self._config, values)
        return self

    @staticmethod
    def get_config_key(config_key_path: 'Union(str, list)' = '', default: 'mixed' = None, \
        configuration: dict = None, env_var: str = None) -> 'mixed':
        """ Get configuration key for the given path """
        if not config_key_path:
            config_key_path = []

        if isinstance(config_key_path, str):
            separator = '.'
            config_key_path = config_key_path.split(separator)

        if not env_var:
            env_var = '_'.join(config_key_path).upper()

        if os.getenv(env_var):
            value = os.getenv(env_var)

            if value.lower() == 'true':
                return True

            if value.lower() == 'false':
                return False

            if value.lower() in ['none', 'null']:
                return None

            return value

        cfg = configuration.copy()

        for _, key in enumerate(config_key_path):
            if key not in cfg:
                return default
            cfg = cfg[key]
        return cfg

Config.Config = Config
sys.modules[__name__] = Config()

"""
Test configuration with Azure Key Vault extension

@author Arttu Manninen <arttu@kaktus.cc>
"""
import os
# import json
# import warnings
# import yaml
from config import Config

config_key = 'test_key'
config_value = 'test-value'
config = Config()

test_prefix = 'test-prefix'

yaml_config = {
    'full': {
        'path': {
            'value': 'foo'
        },
        'path2': {
            'value': 'bar'
        }
    }
}

secrets = {
    'test_key': config_value,
    'test-prefix---test_key': 'prefixed-test-value',
    'test_json': {
        'foo': {
            'bar': 'test'
        }
    },
    'test': {
        'deep': {
            'key': 'deep-key-value'
        }
    }
}

# Store temporarily the system environment values
env_vars = {
    'AZURE_KEYVAULT_ENABLED': None,
    'AZURE_KEYVAULT_URI': None,
    'AZURE_TENANT_ID': None,
    'AZURE_CLIENT_ID': None,
    'AZURE_CLIENT_SECRET': None,
    'AZURE_CLIENT_CERTIFICATE_PATH': None,
    'AZURE_USERNAME': None,
    'AZURE_PASSWORD': None
}

for key, _value in env_vars.items():
    if key in os.environ:
        env_vars[key] = os.environ[key]

class TestConfigWithKeyVault():
    """ Test config with Azure key vault """
    @staticmethod
    def setup():
        """ Test setup """
        if 'AZURE_KEYVAULT_ENABLED' in os.environ:
            del os.environ['AZURE_KEYVAULT_ENABLED']

    @staticmethod
    def teardown():
        """ Test teardown """
        for k, value in env_vars.items():
            if not value:
                continue

            os.environ[k] = value

    @staticmethod
    def test_config_does_not_contain_unset_keyvault_value():
        """ Test that config class reads from keyvault """
        assert config.get(config_key) is None

    @staticmethod
    def test_azure_keyvault_reads_from_keyvault():
        """ Test that Azure Key Vault reads from keyvault """
        os.environ['AZURE_KEYVAULT_ENABLED'] = 'true'
        config.load_secrets()
        assert config.get(config_key) == config_value

    @staticmethod
    def test_load_secrets_does_not_load_anything_when_not_enabled():
        """ Load stored secrets from Azure Key Vault """
        config.set(config_key, None)
        assert config.get(config_key) is None
        config.load_secrets()
        assert config.get(config_key) is None


    @staticmethod
    def test_load_secrets_loads_secretmanager_data():
        """ Load stored secrets from Azure Key Vault """
        config.set('azure.keyvault', {
            'enabled': True
        })

        assert config.get(config_key) is None
        config.load_secrets()
        assert config.get(config_key) == config_value

    @staticmethod
    def test_load_secrets_json_encapsulation_check():
        """ Load JSON encapsulated stored secrets from Azure Key Vault """
        json_config_key = 'test_json'

        config.set('azure.keyvault', {
            'enabled': True,
            'prefix': None
        })

        config.load_secrets()
        assert config.get(json_config_key) == secrets[json_config_key]

    @staticmethod
    def test_load_secrets_skips_when_prefix_mismatch():
        """ Test that load_secrets skips when prefix does not match """
        config.set('azure.keyvault.prefix', 'different-test-prefix')
        config.load_secrets()
        assert config.get(config_key) == config_value

    @staticmethod
    def test_load_secrets_ignores_unprefixed_when_configured():
        """ Test that load_secrets ignores everything but the prefixed when skip_unprefixed """
        unprefixed_config_key = 'test-key'

        config.set('azure.keyvault.prefix', test_prefix)
        config.set('azure.keyvault.skip_unprefixed', True)
        config.set(unprefixed_config_key, None)
        config.load_secrets()
        assert config.get(unprefixed_config_key) is None

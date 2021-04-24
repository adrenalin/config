"""
Test configuration with AWS SecretsManager extension

@author Arttu Manninen <arttu@kaktus.cc>
"""
import os
import json
import warnings
import yaml
from config import Config

# Ignore deprecation warnings for boto3 and moto since there is virtually
# nothing we can do about them
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    from moto import mock_secretsmanager
    import boto3

aws_region = 'eu-north-1'
config_key = 'secret.manager'
config_value = 'secret-value'
config = Config()
config.set('aws.region', aws_region)

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

if 'AWS_SECRETSMANAGER_ENABLED' in os.environ:
    secretsmanager_state = os.environ['AWS_SECRETSMANAGER_ENABLED']
else:
    secretsmanager_state = None

class TestConfigWithSecretsManager():
    """ Test config with AWS SecretsManager """
    @staticmethod
    def setup():
        """ Test setup """
        if 'AWS_SECRETSMANAGER_ENABLED' in os.environ:
            del os.environ['AWS_SECRETSMANAGER_ENABLED']

    @staticmethod
    def teardown():
        """ Test teardown """
        if secretsmanager_state is not None:
            os.environ['AWS_SECRETSMANAGER_ENABLED'] = secretsmanager_state

    @staticmethod
    @mock_secretsmanager
    def test_config_does_not_contain_unset_secretsmanager_value():
        """ Test that config class reads from secretsmanager """
        assert config.get(config_key) is None

    @staticmethod
    @mock_secretsmanager
    def test_boto3_reads_from_secretsmanager():
        """ Test that boto3 reads from secretsmanager """
        client = boto3.client('secretsmanager', aws_region)
        response = client.create_secret(
            Name=config_key,
            SecretString=config_value
        )

        assert response['Name'] == config_key

        secret = client.get_secret_value(SecretId=config_key)
        assert secret['SecretString'] == config_value

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_does_not_load_anything_when_not_enabled():
        """ Load stored secrets from AWS SecretManager """
        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=config_key,
            SecretString=config_value
        )

        assert config.get(config_key) is None
        config.load_secrets()
        assert config.get(config_key) is None


    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_loads_secretmanager_data():
        """ Load stored secrets from AWS SecretManager """
        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=config_key,
            SecretString=config_value
        )

        config.set('aws.secretsmanager', {
            'enabled': True
        })

        assert config.get(config_key) is None
        config.load_secrets()
        assert config.get(config_key) == config_value

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_json_encapsulation_check():
        """ Load JSON encapsulated stored secrets from AWS SecretManager """
        client = boto3.client('secretsmanager', aws_region)
        json_config_key = 'secret_json'
        client.create_secret(
            Name=json_config_key,
            SecretString=json.dumps({
                json_config_key: config_value
            })
        )

        config.set('aws.secretsmanager', {
            'enabled': True,
            'prefix': None
        })

        config.load_secrets()
        assert config.get(json_config_key) == {json_config_key: config_value}

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_yaml_encapsulation_check():
        """ Load YAML encapsulated stored secrets from AWS SecretManager """
        client = boto3.client('secretsmanager', aws_region)
        yaml_config_key = 'secret.yaml'
        yaml_config_value = {
            'yaml': {
                'encapsulation': {
                    'works': True
                }
            }
        }
        client.create_secret(
            Name=yaml_config_key,
            SecretString=yaml.dump(yaml_config_value)
        )

        config.set('aws.secretsmanager', {
            'enabled': True,
            'prefix': None
        })

        config.load_secrets()
        assert config.get(yaml_config_key) == yaml_config_value

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_yaml_encapsulation_check_with_parse_error():
        """ Load YAML encapsulated stored secrets from AWS SecretManager """
        client = boto3.client('secretsmanager', aws_region)
        broken_yaml_config_key = 'secret.yaml_broken'
        broken_yaml = 'text foobar\nnumber: 2'
        client.create_secret(
            Name=broken_yaml_config_key,
            SecretString=broken_yaml
        )

        config.set('aws.secretsmanager.prefix', None)

        config.load_secrets()
        assert config.get(broken_yaml_config_key) == broken_yaml

    @staticmethod
    @mock_secretsmanager
    def test_include_secrets_without_prefix():
        """ Test that load_secrets includes keys without prefix """
        new_config_key = f'new.{config_key}'
        new_config_value = f'new {config_value}'

        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=new_config_key,
            SecretString=new_config_value
        )

        config.set('aws.secretsmanager.prefix', test_prefix)
        config.load_secrets()
        assert config.get(new_config_key) == new_config_value

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_skips_when_prefix_mismatch():
        """ Test that load_secrets skips when prefix does not match """
        prefixed_config_key = f'{test_prefix}@{config_key}'
        prefixed_config_value = 'prefixed-config-value'
        differing_config_key = f'differentprefix@{config_key}'

        config.set('aws.secretsmanager.prefix', test_prefix)
        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=differing_config_key,
            SecretString=config_value
        )
        client.create_secret(
            Name=prefixed_config_key,
            SecretString=prefixed_config_value
        )

        config.set('aws.secretsmanager.prefix', test_prefix)
        config.load_secrets()
        assert config.get(config_key) == prefixed_config_value

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_ignores_unprefixed_when_configured():
        """ Test that load_secrets ignores everything but the prefixed when skip_unprefixed """
        unprefixed_config_key = 'unprefixed.key'
        unprefixed_config_value = 'unprefixed-value'

        config.set('aws.secretsmanager.prefix', test_prefix)
        config.set('aws.secretsmanager.skip_unprefixed', True)
        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=unprefixed_config_key,
            SecretString=unprefixed_config_value
        )

        config.load_secrets()
        assert config.get(unprefixed_config_key) is None

    @staticmethod
    @mock_secretsmanager
    def test_load_secrets_loads_full_config():
        """ Test that load_secrets loads full configuration if it is available """
        prefixed_config_key = f'{test_prefix}@config'

        client = boto3.client('secretsmanager', aws_region)
        client.create_secret(
            Name=prefixed_config_key,
            SecretString=yaml.dump(yaml_config)
        )

        config.set('aws.secretsmanager.prefix', test_prefix)
        config.set('aws.secretsmanager.skip_unprefixed', False)
        config.load_secrets()
        assert config.get('full') == yaml_config['full']

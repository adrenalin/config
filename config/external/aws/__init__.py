"""
Implementation for AWS SecretsManager

@author Arttu Manninen <arttu@kaktus.cc>
"""
import re
import json
import yaml
from config.external.aws.boto3 import Boto3
from config.external.interface import ExternalInterface

boto3 = Boto3()

class AWS(ExternalInterface):
    """ External interface """
    def __init__(self):
        """ Constructor """

    def load(self, config):
        """ Load AWS SecretManager secrets to the configuration """
        prefix = config.get('aws.secretsmanager.prefix', default='')
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

            if config.get('aws.secretsmanager.skip_unprefixed') and (name.find(prefix + '@') != 0):
                continue

            stored_secret = client.get_secret_value(SecretId=name)
            stored_value = self._parse_secret_value(stored_secret['SecretString'])

            # Special case: when the name of the secret is "config" it is handled
            # as a full set of configuration instead of a subset
            if key == 'config':
                config.set(None, stored_value)
                break

            config.set(key, stored_value)

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

"""
Implementation for AWS SecretsManager

@author Arttu Manninen <arttu@kaktus.cc>
"""
import re
import json
import yaml
from config.external.interface import ExternalInterface
from azure.identity import DefaultAzureCredential, ClientSecretCredential, CertificateCredential, UsernamePasswordCredential
from azure.keyvault.secrets import SecretClient

class KeyVault(ExternalInterface):
    SEPARATOR = '---'
    DOT = '--'

    """ External interface """
    def get_credentials(self):
        """ Get credentials """
        tenant_id = self.config.get('azure.tenant_id')
        client_id = self.config.get('azure.client_id')
        client_secret = self.config.get('azure.client_secret')
        certificate_path = self.config.get('azure.client_certificate_path')
        username = self.config.get('azure.username')
        password = self.config.get('azure.password')

        if tenant_id and client_id and client_secret:
            return ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )

        if tenant_id and client_id and certificate_path:
            return CertificateCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                certificate_path=certificate_path
            )

        if client_id and username and password:
            return UsernamePasswordCredential(
                client_id=client_id,
                username=username,
                password=password
            )

        return DefaultAzureCredential()

    def get_client(self):
        """ Get client """
        return SecretClient(
            vault_url=self.config.get('azure.keyvault.uri'),
            credential=self.get_credentials()
        )

    def load(self):
        """ Load Azure Key Vault to the configuration """
        prefix = self.config.get('azure.keyvault.prefix', default='')

        client = self.get_client()

        props = client.list_properties_of_secrets()
        secrets = []

        for prop in props:
            # the list doesn't include values or versions of the secrets
            stored = client.get_secret(prop.name)
            secrets.append({
                'name': prop.name,
                'value': stored.value
            })

        def sort_secrets(secret):
            """ Sort secrets """
            if '---' in secret['name']:
                return 1
            return 0

        secrets.sort(key=sort_secrets)

        for secret in secrets:
            name = secret['name']
            value = self._parse_secret_value(secret['value'])

            if KeyVault.SEPARATOR not in secret['name'] and self.config.get('azure.keyvault.skip_unprefixed'):
                continue

            if KeyVault.SEPARATOR in secret['name']:
                if not prefix or not secret['name'].startswith(f'{prefix}{KeyVault.SEPARATOR}'):
                    continue

                name = name[len(prefix) + len(KeyVault.SEPARATOR)]

            if name == 'config':
                self.config.set(value)
                continue

            self.config.set(name.replace('--', '.').replace('-', '_'), value)

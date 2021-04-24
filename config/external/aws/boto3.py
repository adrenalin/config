"""
Boto3 session interface class

The purpose of this interface class is especially to leverage the Boto3
session to create the clients so that it is possible to separate testing
from production code

@author Arttu Manninen <arttu@kaktus.cc>
"""
import boto3

class Boto3():
    """ Boto3 interface """
    def __init__(self):
        """ Constructor """
        self._session = None
        self._services = {}

    def session(self):
        """ Get Boto3 session """
        if self._session is None:
            self._session = boto3.session.Session()

        return self._session

    def session_reset(self):
        """ Reset the current Boto3 session """
        self._session = None
        self._services.clear()

    def client(self, service_name: str, *args, region: str = 'eu-north-1', **kwargs):
        """ Get Boto3 client using the session """
        if service_name not in self._services:
            self._services[service_name] = self.session() \
                .client(service_name, region, *args, **kwargs)
        return self._services[service_name]

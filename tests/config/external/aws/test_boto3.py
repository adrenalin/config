"""
Test Boto3 session interface

@author Arttu Manninen <arttu@kaktus.cc>
"""
import boto3
from config.external.aws.boto3 import Boto3

boto = Boto3()

class TestBoto3():
    """ Test Boto3 interface """
    @staticmethod
    def test_boto3_can_initialize_session():
        """ Test that Boto3 interface can initialize a session """
        session = boto.session()
        assert isinstance(session, boto3.session.Session)

    @staticmethod
    def test_boto3_session_is_singleton():
        """ Test that Boto3 session is a singleton """
        session_1 = boto.session()
        session_2 = boto.session()
        assert session_1 is session_2

    @staticmethod
    def test_boto3_client_is_singleton():
        """ Test that Boto3 client can connect to a service """
        secrets_manager_1 = boto.client('secretsmanager')
        secrets_manager_2 = boto.client('secretsmanager')
        assert secrets_manager_1 is secrets_manager_2

    @staticmethod
    def test_boto3_session_reset_destroys_singleton_session():
        """ Test that Boto3 client can connect to a service """
        session_1 = boto.session()
        boto.session_reset()
        session_2 = boto.session()
        assert session_1 is not session_2

    @staticmethod
    def test_boto3_client_respects_session_reset():
        """ Test that Boto3 client can connect to a service """
        secrets_manager_1 = boto.client('secretsmanager')
        boto.session_reset()
        secrets_manager_2 = boto.client('secretsmanager')
        assert secrets_manager_1 is not secrets_manager_2

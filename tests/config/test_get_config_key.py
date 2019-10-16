"""
Test get_config_key function

@author Arttu Manninen <arttu@kaktus.cc>
"""
import os
import unittest
from config import Config
config = Config()
get_config_key = config.get_config_key

NESTED_PATH_VALUE = 1
ENVIRONMENT_VALUE = 'set_environment_value'
SHALLOW_VALUE = 5

configuration = {
    'test': {
        'nested': {
            'path': NESTED_PATH_VALUE
        }
    },
    'shallow': SHALLOW_VALUE
}

class TestGetConfigKey(unittest.TestCase):
    """ Test get_config_key """
    @staticmethod
    def test_get_config_key_is_callable():
        """ Test that there is a function called get_config_key """
        assert callable(get_config_key)

    @staticmethod
    def test_get_config_key_returns_shallow():
        """ Test that get_config_key returns the value for "shallow" """
        assert get_config_key('shallow', configuration=configuration) == SHALLOW_VALUE

    @staticmethod
    def test_get_config_key_returns_shallow_dict():
        """ Test that get_config_key returns a dict for "test" """
        assert isinstance(get_config_key('test', configuration=configuration), dict)

    @staticmethod
    def test_get_config_key_returns_default_when_key_does_not_exist():
        """ Test that get_config_key returns default value when key doesn't exist """
        assert get_config_key('imaginary', default=SHALLOW_VALUE, configuration=configuration) \
            == SHALLOW_VALUE

    @staticmethod
    def test_get_config_key_returns_list_path():
        """ Test that get_config_key returns a path provided as an array """
        config_key_path = ['test', 'nested', 'path']
        assert get_config_key(config_key_path, configuration=configuration) \
            == NESTED_PATH_VALUE

    @staticmethod
    def test_get_config_key_returns_nested_string_path():
        """ Test that get_config_key returns a path provided as a string """
        assert get_config_key('test.nested.path', configuration=configuration) \
            == NESTED_PATH_VALUE

    @staticmethod
    def test_get_config_key_returns_nested_partial_string_path():
        """ Test that get_config_key returns a path provided as a string """
        assert get_config_key('test.nested', configuration=configuration)['path'] \
            == NESTED_PATH_VALUE

    @staticmethod
    def test_get_config_key_returns_environment_variable_if_available():
        """ Test that get_config_key returns environment variable first if it is available """
        os.environ['TEST_GET_CONFIG_KEY_ENVIRONMENT_VALUE'] = ENVIRONMENT_VALUE
        assert get_config_key(
            'shallow',
            env_var='TEST_GET_CONFIG_KEY_ENVIRONMENT_VALUE',
            configuration=configuration
        ) == ENVIRONMENT_VALUE

    @staticmethod
    def test_get_config_key_returns_string_true_typecasted_as_boolean():
        """ Test that get_config_key returns string true typecasted as boolean """
        os.environ['TEST_GET_CONFIG_KEY_BOOLEAN'] = 'true'
        assert get_config_key(
            'shallow',
            env_var='TEST_GET_CONFIG_KEY_BOOLEAN',
            configuration=configuration
        ) is True

    @staticmethod
    def test_get_config_key_returns_string_false_typecasted_as_boolean():
        """ Test that get_config_key returns string false typecasted as boolean """
        os.environ['TEST_GET_CONFIG_KEY_BOOLEAN'] = 'false'
        assert get_config_key(
            'shallow',
            env_var='TEST_GET_CONFIG_KEY_BOOLEAN',
            configuration=configuration
        ) is False

    @staticmethod
    def test_get_config_key_returns_string_none_typecasted_as_boolean():
        """ Test that get_config_key returns string none typecasted as boolean """
        os.environ['TEST_GET_CONFIG_KEY_BOOLEAN'] = 'none'
        assert get_config_key(
            'shallow',
            env_var='TEST_GET_CONFIG_KEY_BOOLEAN',
            configuration=configuration
        ) is None

    @staticmethod
    def test_get_config_key_returns_string_null_typecasted_as_boolean():
        """ Test that get_config_key returns string null typecasted as boolean """
        os.environ['TEST_GET_CONFIG_KEY_BOOLEAN'] = 'null'
        assert get_config_key(
            'shallow',
            env_var='TEST_GET_CONFIG_KEY_BOOLEAN',
            configuration=configuration
        ) is None

    def test_get_config_key_without_config_key_path_returns_everything(self):
        """ Test that get_config_key without a value returns full config """
        self.assertDictEqual(configuration, get_config_key(configuration=configuration))

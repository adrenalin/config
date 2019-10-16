"""
Tests for configuration

@author Arttu Manninen <arttu@kaktus.cc>
"""
import os
import unittest
import pytest
from config import Config

current_path = os.path.dirname(os.path.realpath(__file__))
main_configuration_path = os.path.join(current_path, 'files', 'main.yml')
extended_configuration_path = os.path.join(current_path, 'files', 'extended.yml')
invalid_configuration_path = os.path.join(current_path, 'files', 'invalid.yml')

config = Config()

class TestConfig(unittest.TestCase):
    """ Test cache interface class """
    @staticmethod
    def test_config_class():
        """ Test that there is a cache interface class """
        assert config is not None

    @staticmethod
    def test_get_is_callable():
        """ Test that there is a method called get """
        assert callable(config.get)

    @staticmethod
    def test_load_configuration_is_callable():
        """ Test that there is a method called load_configuration """
        assert callable(config.load_configuration)

    @staticmethod
    def test_load_configuration_loads_main_file():
        """ Test that load_configuration loads main file """
        config.load_configuration(main_configuration_path)
        assert config.get('test.nested.path.value') == 'test value'

    @staticmethod
    def test_load_configuration_extends_the_previous():
        """ Test that load_configuration extends the configuration """
        config.load_configuration(extended_configuration_path)
        assert config.get('test.nested.path.value') == 'overriding test value'

    @staticmethod
    def test_load_configuration_raises_an_exception_when_file_does_not_exist():
        """ Test that load_configuration raises an exception if file doesn't exist """
        with pytest.raises(FileNotFoundError):
            config.load_configuration(invalid_configuration_path)

    @staticmethod
    def test_load_configuration_fails_gracefully_when_file_does_not_exist():
        """ Test that load_configuration fails gracefully when requested to """
        config.load_configuration(invalid_configuration_path, graceful=True)
        assert True

    @staticmethod
    def test_set_with_shallow_path():
        """ Test setting a config key with shallow path """
        shallow_key_path = 'shallow_key_path'
        test_value = 'shallow key path value'

        config.set(shallow_key_path, test_value)
        assert config.get(shallow_key_path) == test_value

    @staticmethod
    def test_set_with_deep_key_path_with_string():
        """ Test setting a deep key path to config """
        deep_key_path = 'deep.key.path'
        test_value = 'deep key path value'

        config.set(deep_key_path, test_value)
        assert isinstance(config.get('deep'), dict)
        assert config.get(deep_key_path) == test_value

    @staticmethod
    def test_set_with_deep_key_path_with_list():
        """ Test setting a deep key path to config """
        deep_key_path = ('second', 'deep', 'key', 'path')
        test_value = 'second deep key path value'

        config.set(deep_key_path, test_value)
        assert isinstance(config.get('second'), dict)
        assert config.get(deep_key_path) == test_value

    @staticmethod
    def test_set_returns_self():
        """ Test that set returns self for chaining purposes """
        return_value = config.set('returns_self', True)
        assert return_value is config

    def test_set_without_path_sets_the_root(self):
        """ Test that setting without a config key path sets to the root """
        mock_config = {'foo': 'bar'}
        root_config = Config()
        root_config.set(value=mock_config)
        self.assertDictEqual(root_config.get(), mock_config)

    @staticmethod
    def test_get_returns_implicit_environment_value_when_available():
        """ Test that get_config_key returns implicit environment value if available """
        deep_key_path = 'deep.key.implicit'
        deep_key_value = 'Default value'

        deep_key_env_var_path = 'DEEP_KEY_IMPLICIT'
        deep_key_env_var_value = 'Environment value'

        os.environ[deep_key_env_var_path] = deep_key_env_var_value

        config.set('deep_key_path', deep_key_value)
        assert config.get(deep_key_path) == deep_key_env_var_value

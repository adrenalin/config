"""
Test importing config singleton
"""

instances = {}
test_path = 'foo.bar'
test_value = ['foo', 'bar']

class TestConfigSingleton():
    """ Test config singleton """
    @staticmethod
    def test_config_is_callable():
        """ Test that config is callable """
        import config
        assert isinstance(config, config.Config)
        config.set(test_path, test_value)
        instances['config'] = config

    @staticmethod
    def test_config_is_singleton():
        """ Test that config is callable """
        import config
        assert config == instances['config']
        assert config.get(test_path) == test_value

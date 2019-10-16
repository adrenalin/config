"""
Test merge function

@author Arttu Manninen <arttu@kaktus.cc>
"""
from config.merge import merge
import numpy

class TestMerge():
    """ Test merge function """
    @staticmethod
    def test_merge_raises_exception_with_no_arguments():
        """ Test that merge fails with no arguments """
        try:
            merge()
        except AssertionError:
            assert True
            return
        assert False

    @staticmethod
    def test_merge_raises_exception_with_one_argument():
        """ Test that merge fails with only one argument """
        try:
            merge({'foo', 'bar'})
        except AssertionError:
            assert True
            return
        assert False

    @staticmethod
    def test_merge_requires_dicts():
        """ Test that merge requires all arguments to be dictionaries """
        try:
            merge('foo', 'bar')
        except AssertionError:
            assert True
            return
        assert False

    @staticmethod
    def test_merge_with_shallow_dicts_shared_keys():
        """ Test merge function with shallow dictionaries with shared keys """
        merged = merge({'foo': 'bar'}, {'foo': 'foo'})
        assert merged['foo'] == 'foo'

    @staticmethod
    def test_merge_with_shallow_dicts_not_shared_keys():
        """ Test merge function with shallow dictionaries withot shared keys """
        merged = merge({'foo': 'bar'}, {'bar': 'foo'})
        assert merged['foo'] == 'bar'
        assert merged['bar'] == 'foo'

    @staticmethod
    def test_merge_with_deep_dicts():
        """ Test merge function with shallow dictionaries """
        merged = merge({'deep': {'nested': {'structure': True}}}, {'foo': 'foo'})
        assert merged['deep']['nested']['structure']

    @staticmethod
    def test_merge_with_deep_does_not_use_pointers():
        """ Test merge function with shallow dictionaries """
        dict_1 = {
            'deep': {
                'nested': {
                    'structure': True
                }
            }
        }
        dict_2 = {
            'deep': {
                'nested': {
                    'structure': False
                }
            }
        }

        merged = merge(dict_1, dict_2)
        assert merged['deep']['nested'] is not dict_1['deep']['nested']
        assert merged['deep']['nested'] is not dict_2['deep']['nested']

    @staticmethod
    def test_merge_accepts_lists():
        """ Test merging lists """
        dict_1 = {
            'list': ['foo', 'bar']
        }
        dict_2 = {
            'list': ['boo', 'far']
        }
        merged = merge(dict_1, dict_2)
        assert numpy.array_equal(
            merged['list'], ['foo', 'bar', 'boo', 'far']
        )

    @staticmethod
    def test_merge_scraps_duplicates_in_lists():
        """ Test merging lists """
        dict_1 = {
            'list': ['foo', 'bar']
        }
        dict_2 = {
            'list': ['bar', 'far']
        }
        merged = merge(dict_1, dict_2)
        assert numpy.array_equal(
            merged['list'], ['foo', 'bar', 'far']
        )

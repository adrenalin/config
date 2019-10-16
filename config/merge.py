"""
Deep merge enumerable objects

Merging will create a deep copy of the objects and will not maintain the
reference.

Dictionaries will keep the keys from all the members and values from last
argument. Lists and arrays will be merged as union, but maintaining the value
order.

Merging::

    dict1 = {
        'deep': {
            'path': true
            'first': 'dict1'
        },
        'list': (
            'value1',
            'value2'
        )
    }

    dict2 = {
        'deep': {
            'path': false,
            'second': 'dict2'
        },
        'list': (
            'value2',
            'value3'
        ),
        'shallow': 'value'
    }

    merged = merge(dict1, dict2)

    # Will yield
    merged = {
        'deep': {
            'path': false,
            'first': 'dict1',
            'second': 'dict2'
        },
        'list': (
            'value1',
            'value2',
            'value3'
        ),
        'shallow': 'value'
    }

@author Arttu Manninen <arttu@kaktus.cc>
"""
def merge(*args: dict) -> dict:
    """ Merge two or more iterables """
    if len(args) < 2:
        raise AssertionError('Merge requires at least two arguments')

    assert isinstance(args[0], dict)
    target = args[0].copy()
    args = args[1:]

    for _i, arg in enumerate(args):
        assert isinstance(arg, dict)

        for key, value in arg.items():
            if isinstance(value, dict):
                node = target.setdefault(key, {}).copy()
                target[key] = merge(node, value)
                continue

            if key not in target:
                target[key] = None

            # Merge arrays
            if isinstance(target[key], list) and isinstance(value, list):
                # Create a shallow copy so that the original does not change
                target[key] = target[key] + [v for v in value if v not in target[key]]
                # resulting_list.extend(x for x in second_list if x not in resulting_list)
                continue

            target[key] = value
    return target

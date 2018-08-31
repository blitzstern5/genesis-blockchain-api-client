from nose import with_setup

from genesis_blockchain_api_client.utils import camel_to_snake

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_camel_to_snake():
    m = {
        'CamelStyle': 'camel_style',
        '1ThisIsATest': '1_this_is_a_test',
    }
    for src, dst_exp in m.items():
        assert camel_to_snake(src) == dst_exp

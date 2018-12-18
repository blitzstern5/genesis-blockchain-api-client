from nose import with_setup

from genesis_blockchain_api_client.backend.versions import (
    NoSuchBackendVersionError,
    NoSuchBackendFeatureError,
    get_features,
    feature_to_options,
    version_to_options,
    version_features_map,
    feature_options_map,
    get_available_versions,
    get_latest_version,
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_available_versions():
    assert get_available_versions() == ('201802XX', '20180512', '201806XX', '20180830', '20180902')

@with_setup(my_setup, my_teardown)
def test_get_latest_version():
    for i in range(0, 30):
        assert get_latest_version() == '20180902'

@with_setup(my_setup, my_teardown)
def test_get_features():
    try:
        get_features('NO_EXISTEN')
    except NoSuchBackendVersionError as e:
        assert isinstance(e, NoSuchBackendVersionError) \
               and str(e) == 'NO_EXISTEN'

    for version in version_features_map:
        assert get_features(version) == version_features_map[version]['features']

@with_setup(my_setup, my_teardown)
def test_feature_to_options():
    try:
        feature_to_options('NO_EXISTEN')
    except NoSuchBackendFeatureError as e:
        assert isinstance(e, NoSuchBackendFeatureError) \
               and str(e) == 'NO_EXISTEN'

    for feature, content in feature_options_map.items():
        assert feature_to_options(feature) == content['options']

@with_setup(my_setup, my_teardown)
def test_version_to_options():
    try:
        version_to_options('NO_EXISTEN')
    except NoSuchBackendVersionError as e:
        assert isinstance(e, NoSuchBackendVersionError) \
               and str(e) == 'NO_EXISTEN'

    options = version_to_options('201802XX')
    assert options == {
        'use_signtest': True,
        'sign_fmt': 'RAW',
        'pub_key_fmt': 'RAW',
        'use_login_prefix': False,
        'use_request_id': False,
    }

    options = version_to_options('201806XX')
    assert options == {
        'use_signtest': False,
        'sign_fmt': 'DER',
        'use_login_prefix': True,
        'pub_key_fmt': 'RAW',
        'use_request_id': True,
    }

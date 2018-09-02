feature_options_map = {
    'login_prefix_in_login_call': {
        'desc': "use LOGIN + UID in /login calls",
        'options': {
            'use_login_prefix': True,
        },
        'targets': ('api-client',),
    },
    'signtest_api_endpoint': {
        'desc': "/api/v2/signtest is present",
        'options': {
            'use_signtest': True,
        },
        'targets': ('api-client',),
    },
    'raw_sign_fmt': {
        'desc': "only raw signature format is supported",
        'options': {
            'sign_fmt': 'RAW',
        },
        'targets': ('api-client',),
    },
    'der_sign_fmt': {
        'desc': "only DER signature format is supported",
        'options': {
            'sign_fmt': 'DER',
        },
        'targets': ('api-client',),
    },
    'raw_pub_key_fmt': {
        'desc': "only raw public key format is supported",
        'options': {
            'pub_key_fmt': 'RAW',
        },
        'targets': ('api-client',),
    },
    'request_id_in_contract_calls': {
        'desc': "use prepare(contract) -> requist_id -> /contract( request_id)",
        'options': {
            'use_request_id': True,
        },
        'targets': ('api-client',),
    },
    'blocks_api_endpoint': {
        'desc': "/blocks api endpoint to fetch block internals data",
        'options': {},
        'targets': ('api-client',),
    },
    'blocks_api_endpoint_base64_snakes': {
        'desc': "/blocks api endpoint to fetch block internals data with base64 encoded hashes and snake-style key names",
        'options': {},
        'targets': ('api-client',),
    },

    'system_parameters_at_ecosystem': {
        'desc': "previously were at system_parameters table",
        'options': {},
        'targets': ('block-explorer',),
    },
    'image_id_instead_of_avatar': {
        'desc': "image_id instead of avatar field",
        'options': {},
        'targets': ('block-explorer',),
    },
    'member_info_at_members': {
        'desc': "previously were at system_parameters table",
        'options': {},
        'targets': ('block-explorer',),
    },
}

version_features_map = {
    '201802XX': {
        'features': (
            'signtest_api_endpoint',
            'raw_sign_fmt',
            'raw_pub_key_fmt',
        ),
    },
    '20180512': {
        'git': {
            'branch': 'develop',
             'commmit': '4b69b8e',
             'repo': 'https://github.com/GenesisKernel/go-genesis/pull/290',
        },
        'features': (
            'system_parameters_at_ecosystem',
            'member_info_at_members',
        ),
    },
    '201806XX': {
        'features': (
            'system_parameters_at_ecosystem',
            'image_id_instead_of_avatar',
            'member_info_at_members',
            'login_prefix_in_login_call',
            'der_sign_fmt',
            'raw_pub_key_fmt',
            'request_id_in_contract_calls',
        ),
    },
    '20180830': {
        'git': {
            'repo': 'https://github.com/GenesisKernel/go-genesis/pull/513',
            'branch': 'master',
            'commmit': 'e5ddc76',
        },
        'features': (
            'system_parameters_at_ecosystem',
            'image_id_instead_of_avatar',
            'member_info_at_members',
            'login_prefix_in_login_call',
            'der_sign_fmt',
            'raw_pub_key_fmt',
            'request_id_in_contract_calls',
            'blocks_api_endpoint',
        ),
    },
    '20180902': {
        'git': {
            'repo': 'https://github.com/blitzstern5/go-genesis',
            'branch': 'feature/block-txs-info-fixes ',
            'commmit': '9e4ddbc',
        },
        'features': (
            'system_parameters_at_ecosystem',
            'image_id_instead_of_avatar',
            'member_info_at_members',
            'login_prefix_in_login_call',
            'der_sign_fmt',
            'raw_pub_key_fmt',
            'request_id_in_contract_calls',
            'blocks_api_endpoint_base64_snakes',
        ),
    },
}

default_options = {
    'use_signtest': False,
    'use_login_prefix': False,
    'sign_fmt': 'DER',
    'pub_key_fmt': 'RAW',
    'use_request_id': False,
}

class NoSuchBackendVersionError(Exception):
    pass

class NoSuchBackendFeatureError(Exception):
    pass

def get_available_versions():
    return tuple(version_features_map.keys())

def get_latest_version():
    versions = get_available_versions()
    return versions[-1] if versions else None

def get_features(backend_version):
    if backend_version in version_features_map:
        return version_features_map[backend_version]['features']
    else:
        raise NoSuchBackendVersionError(backend_version)

def feature_to_options(feature):
    if feature in feature_options_map:
        return feature_options_map[feature]['options']
    else:
        raise NoSuchBackendFeatureError(feature)

def version_to_options(backend_version):
    all_options = {}
    all_options.update(default_options)
    for feature in get_features(backend_version):
        all_options.update(feature_to_options(feature))
    return all_options



d0 = [
    {
        'id': '123',
        'txs': [
            {
                'hash': '123123',
                'contract_name': 'Contract1',
                'params': {'name1': 'val1', 'name2': 'val2'},
                'key_id': '123123123',
            },
            {
                'hash': '123456',
                'contract_name': 'Contract2',
                'params': {'name3': 'val3', 'name4': 'val4'},
                'key_id': '123123456',
            }
        ]
    },
    {
        'id': '456',
        'txs': [
            {
                'hash': '456456',
                'contract_name': 'Contract3',
                'params': {'name5': 'val5', 'name6': 'val6'},
                'key_id': '456456456',
            },
            {
                'hash': '456789',
                'contract_name': 'Contract4',
                'params': {'name6': 'val6', 'name7': 'val7'},
                'key_id': '456456789',
            }
        ]
    },
]

d1 = [
    {
        '123': [
            {
                'Hash': '123123',
                'ContractName': 'Contract1',
                'Params': {'ParamName1': 'val1', 'ParamName2': 'val2'},
                'KeyID': '123123123',
            },
            {
                'Hash': '123456',
                'ContractName': 'Contract2',
                'Params': {'ParamName3': 'val3', 'ParamName4': 'val4'},
                'KeyID': '123123456',
            }
        ]
    },
    {
        '456': [
            {
                'Hash': '456456',
                'ContractName': 'Contract3',
                'Params': {'ParamName5': 'val5', 'ParamName6': 'val6'},
                'KeyID': '456456456',
            },
            {
                'Hash': '456789',
                'ContractName': 'Contract4',
                'Params': {'ParamName6': 'val6', 'ParamName7': 'val7'},
                'KeyID': '456456789',
            }
        ]
    },
]

def blocks_list_to_dict(l):
    _dict = {}
    for d in l:
        block_id = tuple(d.keys())[0]
        _dict[block_id] = d[block_id]
    return _dict

d2 = blocks_list_to_dict(d1)

def get_txs(d):
    return d[tuple(d.keys())[0]]


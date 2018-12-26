import os
import logging.config

import json
try:
    import yaml
except ImportError:
    import ruamel.yaml as yaml

def setup_logging(path='logging.yaml', level=logging.ERROR, env_key='LOG_CFG',
                  level_env_key='LOG_LEVEL', fmt="yaml"):
    if not fmt:
        ext = path.split('.')[-1]
        if ext in ['json', 'yaml']:
            fmt = ext
    value = os.getenv(env_key, None)
    if value:
        path = value
    if level_env_key:
        _level = os.getenv(level_env_key, '').lower()
        if _level in ['20', 'i', 'inf', 'info']:
            level = logging.INFO
        elif _level in ['30', 'w', 'warn', 'warning']:
            level = logging.WARNING
        elif _level in ['10', 'd', 'deb', 'debug']:
            level = logging.DEBUG
        elif _level in ['40', 'e', 'err', 'error']:
            level = logging.ERROR
        elif _level in ['50', 'c', 'crit', 'critical']:
            level = logging.CRITICAL
        elif _level in ['0', 'n', 'not', 'notset']:
            level = logging.NOTSET
    if os.path.exists(path):
        with open(path, 'rt') as f:
            if fmt == "json":
                config = json.load(f)
            elif fmt == "yaml":
                config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)


import os
import logging.config

import json
try:
    import yaml
except ImportError:
    import ruamel.yaml as yaml

def setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOG_CFG',
                  fmt="yaml"):
    if not fmt:
        ext = path.split('.')[-1]
        if ext in ['json', 'yaml']:
            fmt = ext
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            if fmt == "json":
                config = json.load(f)
            elif fmt == "yaml":
                config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)


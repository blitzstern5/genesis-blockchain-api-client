Some tests require private key to start. Use it like this:
```
GENESIS_FOUNDER_PRIV_KEY=3210931280328109312 nosetests -s
```
or
```
LOG_CFG=tests/logger.yaml APLA_FOUNDER_PRIV_KEY=3210931280328109312 nosetests -s
```

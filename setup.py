import os

from setuptools import setup, find_packages

__VERSION__ = '0.1.0'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'mock',
    'nose',
    'requests',
    'requests_toolbelt',
    'urllib3',
    'ruamel.yaml',
    #'PyYAML',
    'genesis-blockchain-tools',
]

dependency_links = [
    'git+https://github.com/blitzstern5/genesis-blockchain-tools#egg=genesis-blockchain-tools',
    'git+https://github.com/requests/requests#egg=requests',
]

setup(
    name='genesis_blockchain_api_client',
    version=__VERSION__,
    description='Genesis BlockChain API Client',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: Blockchain",
    ],
    author='blitzstern5',
    author_email='blitzstern5@gmail.com',
    url='https://github.com/blitzstern5/genesis-blockchain-api-client',
    keywords='crypto blockchain genesis tools',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='genesis_blockchain_api_client',
    install_requires=requires,
    dependency_links=dependency_links,
)

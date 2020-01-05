import os

from setuptools import setup, find_packages

__VERSION__ = '0.4.2'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()


setup(
    name='genesis_blockchain_api_client',
    version=__VERSION__,
    description='Genesis BlockChain API Client',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: Blockchain",
    ],
    license='MIT',
    author='blitzstern5',
    author_email='blitzstern5@gmail.com',
    url='https://github.com/blitzstern5/genesis-blockchain-api-client',
    keywords='crypto blockchain genesis api client',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3',
    setup_requires=['nose >= 1.3.7'],
    install_requires=[
        'requests>=2.22.0',
        'requests-toolbelt>=0.9.1',
        'urllib3>=1.25.3',
        'PyYAML>=5.1.1',
        'ruamel.yaml>=0.15.99',
        'puremagic>=1.5',
        'genesis-blockchain-tools>=0.4.1',
    ],
    dependency_links=[
        'git+https://github.com/blitzstern5/genesis-blockchain-tools#egg=genesis-blockchain-tools',
    ],
    tests_require=["nose >= 1.3.7", "mock >= 3.0.5"],
    extras_require={
        'testing': ["nose >= 1.3.7", "mock >= 3.0.5"],
    },

)
#    test_suite='genesis_blockchain_api_client',

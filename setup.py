from setuptools import setup, find_packages

setup(
    name='option_parser',
    version='0.11',
    packages=find_packages(),
    install_requires=[
        'typed_argument_parser @ git+https://github.com/vphpersson/typed_argument_parser.git#egg=typed_argument_parser',
        'toml'
    ]
)

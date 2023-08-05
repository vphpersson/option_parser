from logging import Logger, getLogger
from typing import Final, Any, Self
from abc import ABC, abstractmethod
from os import environ as os_environ
from pathlib import Path
from functools import cached_property

from typed_argument_parser import TypedArgumentParser
from tomllib import loads as toml_loads


LOG: Final[Logger] = getLogger(__name__)


class OptionParserNamespace(ABC):
    def __setattr__(self, key, value):
        if annotation_type := self.__annotations__.get(key):
            if value is not None and annotation_type in {str, int, float} and not isinstance(value, annotation_type):
                value = annotation_type(value)

            super().__setattr__(key, value)
        else:
            raise ValueError(f'Key "{key}" is not present in the namespace\'s annotations.')


class OptionParser(TypedArgumentParser, ABC):

    @abstractmethod
    class Namespace(OptionParserNamespace):
        pass

    @property
    def module_name(self):
        return self.__module__.split(sep='.')[0]

    @cached_property
    def config_path(self):
        # TODO: Choose a directory depending on the OS?
        return Path.home() / '.config' / self.module_name / f'{self.module_name}.toml'

    def read_config(self, path: str | Path | None = None, raise_exception: bool = True) -> dict[str, Any]:
        """
        Read a configuration from a file.

        :param path: The path of the configuration file to be read.
        :param raise_exception: Whether to raise an exception in case the configuration file cannot be read.
        :return: The configuration read from the file.
        """

        path = Path(path) if path is not None else self.config_path

        config: dict[str, Any] = {}

        try:
            config = toml_loads(path.read_text())
        except FileNotFoundError as e:
            if raise_exception:
                raise e
            LOG.debug(msg='The configuration file could not be read because it could not be found.', exc_info=e)
        except Exception as e:
            if raise_exception:
                raise e
            LOG.warning(msg='Could not read the configuration file.', exc_info=e)

        return config

    def read_environment(self) -> dict[str, Any]:

        env_prefix: str = f'{self.module_name.upper()}_'

        return {
            key.removeprefix(env_prefix).lower(): value
            for key, value in os_environ.items()
            if key.startswith(env_prefix)
        }

    def parse_options(
        self,
        parse_args: bool = True,
        read_config: bool = True,
        read_environment: bool = True,
        parse_args_options: dict[str, Any] | None = None,
        read_config_options: dict[str, Any] | None = None,
    ) -> 'OptionParser.Namespace':

        option_parser_namespace: OptionParser.Namespace

        if parse_args:
            option_parser_namespace = self.parse_args(**(parse_args_options or {}))
        else:
            option_parser_namespace = self.Namespace()

        if read_config:
            for key, value in self.read_config(**(read_config_options or {})).items():
                # option_parser_namespace.__setattr__(key, value)
                setattr(option_parser_namespace, key, value)

        if read_environment:
            for key, value in self.read_environment().items():
                setattr(option_parser_namespace, key, value)

        return option_parser_namespace


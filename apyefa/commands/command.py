import logging
from abc import abstractmethod

from voluptuous import MultipleInvalid, Schema

from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaFormatNotSupported, EfaParameterError
from apyefa.helpers import is_date, is_datetime, is_time

_LOGGER = logging.getLogger(__name__)


class Command:
    def __init__(self, name: str, macro: str, output_format: str = "rapidJSON") -> None:
        self._name: str = name
        self._macro: str = macro
        self._parameters: dict[str, str] = {}
        self._format: str = output_format

        self.add_param("outputFormat", output_format)
        self.add_param("coordOutputFormat", "WGS84")

    def add_param(self, param: str, value: str):
        if not param or not value:
            return

        if param not in self._get_params_schema().schema.keys():
            raise EfaParameterError(
                f"Parameter {param} is now allowed for this command"
            )

        _LOGGER.debug(f'Add parameter "{param}" with value "{value}"')

        self._parameters.update({param: value})

        _LOGGER.debug("Updated parameters:")
        _LOGGER.debug(self._parameters)

    def add_param_datetime(self, date: str):
        if not date:
            return

        if is_datetime(date):
            self.add_param("itdDate", date.split(" ")[0])
            self.add_param("itdTime", date.split(" ")[1].replace(":", ""))
        elif is_date(date):
            self.add_param("itdDate", date)
        elif is_time(date):
            self.add_param("itdTime", date.replace(":", ""))
        else:
            raise ValueError("Date(time) provided in invalid format")

    def to_str(self) -> str:
        self._parameters = self.extend_with_defaults()
        self.validate()

        return f"{self._name}?commonMacro={self._macro}" + self._get_params_as_str()

    def __str__(self) -> str:
        return self.to_str()

    def validate(self):
        """Validate self._parameters

        Raises:
            EfaParameterError: some of parameters are missing or have invalid values
        """
        params_schema = self._get_params_schema()

        try:
            params = self.extend_with_defaults()
            params_schema(params)
        except MultipleInvalid as exc:
            _LOGGER.error("Parameters validation failed", exc_info=exc)
            raise EfaParameterError(str(exc)) from exc

    def extend_with_defaults(self) -> dict:
        """Extend self._parameters with default values

        Returns:
            dict: parameters extended with default values
        """

        params_schema = self._get_params_schema()

        return params_schema(self._parameters)

    def _get_params_as_str(self) -> str:
        """Return parameters concatenated with &

        Returns:
            str: parameters as string
        """
        if not self._parameters:
            return ""

        return "&" + "&".join([f"{k}={str(v)}" for k, v in self._parameters.items()])

    @abstractmethod
    def parse(self, data: str):
        raise NotImplementedError("Abstract method not implemented")

    @abstractmethod
    def _get_params_schema(self) -> Schema:
        raise NotImplementedError("Abstract method not implemented")

    @abstractmethod
    def _get_parser(self):
        match self._format:
            case "rapidJSON":
                return RapidJsonParser()
            case _:
                raise EfaFormatNotSupported(
                    f"Output format {self._format} is not supported"
                )

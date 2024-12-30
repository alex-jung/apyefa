import logging
from abc import abstractmethod
from datetime import date, datetime

from voluptuous import MultipleInvalid, Schema

from apyefa.commands.parsers.rapid_json_parser import RapidJsonParser
from apyefa.exceptions import EfaFormatNotSupported, EfaParameterError
from apyefa.helpers import is_date, is_datetime, is_time

_LOGGER = logging.getLogger(__name__)


class Command:
    def __init__(self, name: str, format: str) -> None:
        self._name: str = name
        self._parameters: dict[str, str] = {}
        self._format = format

        self.add_param("outputFormat", format)

    def add_param(self, param: str, value: str | bool):
        """
        Adds a parameter and its value to the command's parameters.

        Args:
            param (str): The name of the parameter to add.
            value (str | bool): The value of the parameter. If the value is a boolean,
                                it will be converted to "1" for True and "0" for False.

        Raises:
            EfaParameterError: If the parameter is not allowed for this command.
        """
        if not param or value is None:
            return

        _LOGGER.debug(f'Add parameter "{param}" with value "{value}"')

        if isinstance(value, bool):
            value = "1" if value else "0"

        self._parameters.update({param: value})

        _LOGGER.debug("Updated parameters:")
        _LOGGER.debug(self._parameters)

    def add_param_datetime(self, arg_date: str | datetime | date):
        """
        Adds date and/or time parameters to the command based on the provided argument.

        Parameters:
        arg_date (str | datetime | date): The date and/or time to be added. It can be a string, datetime object, or date object.

        Raises:
        ValueError: If the provided date(time) is in an invalid format.

        Notes:
        - If arg_date is a datetime object, both date and time parameters are added.
        - If arg_date is a date object, only the date parameter is added.
        - If arg_date is a string, it will be checked if it is a valid datetime, date, or time string.
        """
        if not arg_date:
            return

        if isinstance(arg_date, datetime):
            self.add_param("itdDate", arg_date.strftime("%Y%m%d"))
            self.add_param("itdTime", arg_date.strftime("%H%M"))
        elif isinstance(arg_date, date):
            self.add_param("itdDate", arg_date.strftime("%Y%m%d"))
        elif is_datetime(arg_date):
            self.add_param("itdDate", arg_date.split(" ")[0])
            self.add_param("itdTime", arg_date.split(" ")[1].replace(":", ""))
        elif is_date(arg_date):
            self.add_param("itdDate", arg_date)
        elif is_time(arg_date):
            self.add_param("itdTime", arg_date.replace(":", ""))
        else:
            raise ValueError(f'Date(time) "{arg_date}" provided in invalid format')

    def validate_params(self):
        """
        Validates the parameters against the schema.

        Raises:
            EfaParameterError: If the parameters are invalid
        """

        try:
            self._get_params_schema()(self._parameters)
        except MultipleInvalid as e:
            raise EfaParameterError(f"Invalid parameter(s) detected: {str(e)}")

    def __str__(self) -> str:
        return f"{self._name}" + self._get_params_as_str()

    def _get_params_as_str(self) -> str:
        """
        Converts the parameters dictionary to a query string.

        If the parameters dictionary is empty, returns an empty string.
        Otherwise, returns a string starting with '?' followed by the
        parameters in 'key=value' format, joined by '&'.

        Returns:
            str: The query string representation of the parameters.
        """
        if not self._parameters:
            return ""

        return "?" + "&".join([f"{k}={str(v)}" for k, v in self._parameters.items()])

    @abstractmethod
    def parse(self, data: str):
        """
        Parses the given data.

        Args:
            data (str): The data to be parsed.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Abstract method not implemented")

    @abstractmethod
    def _get_params_schema(self) -> Schema:
        """
        Retrieve the schema for the parameters.

        This is an abstract method that should be implemented by subclasses
        to provide the specific schema for the parameters.

        Returns:
            Schema: The schema for the parameters.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Abstract method not implemented")

    @abstractmethod
    def _get_parser(self):
        """
        Returns the appropriate parser based on the specified format.

        This method uses a match-case statement to determine which parser to return
        based on the value of the instance variable `self._format`.

        Returns:
            RapidJsonParser: If the format is "rapidJSON".

        Raises:
            EfaFormatNotSupported: If the format is not supported.
        """
        match self._format:
            case "rapidJSON":
                return RapidJsonParser()
            case _:
                raise EfaFormatNotSupported(
                    f"Output format {self._format} is not supported"
                )

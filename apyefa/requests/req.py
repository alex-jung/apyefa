import logging
from abc import abstractmethod

from voluptuous import MultipleInvalid, Schema

from apyefa.exceptions import EfaParameterError, EfaResponseInvalid
from apyefa.helpers import is_date, is_datetime, is_time

_LOGGER = logging.getLogger(__name__)


class Request:
    def __init__(self, name: str, macro: str, output_format: str = "rapidJSON") -> None:
        self._name: str = name
        self._macro: str = macro
        self._parameters: dict[str, str] = {}
        self._schema: Schema = self._get_params_schema()

        self.add_param("outputFormat", output_format)

    def add_param(self, param: str, value: str):
        if not param or not value:
            return

        if param not in self._get_params_schema().schema.keys():
            raise EfaParameterError(
                f"Parameter {param} is now allowed for this request"
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

    def __str__(self) -> str:
        """Validate parameters schema and return parameters as string\n
        for URL parametrization

        Returns:
            str: parameters as string ready to use in URL
        """

        self._parameters = self._validate_params(self._parameters)

        return f"{self._name}?commonMacro={self._macro}" + self._params_str()

    def _validate_params(self, params: dict) -> dict:
        """Validate parameters stored for request. This step will extend parameters with default values
        as well.

        Returns:
            str: Validated and extended with default value parameters dict

        Raises:
            EfaParameterError: Validation of some parameter(s) failed
        """
        try:
            return self._schema(params)
        except MultipleInvalid as exc:
            _LOGGER.error("Parameters validation failed", exc_info=exc)
            raise EfaParameterError(str(exc)) from exc

    def _validate_response(self, response: dict) -> None:
        val_schema = self._get_response_schema()

        try:
            val_schema(response)
        except MultipleInvalid as exc:
            raise EfaResponseInvalid(
                f"Server response validataion failed - {str(exc)}"
            ) from None

    def _params_str(self) -> str:
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
    def _get_response_schema(self) -> Schema:
        raise NotImplementedError("Abstract method not implemented")

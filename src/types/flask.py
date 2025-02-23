from typing import TypeVar, Union, Tuple, Any
from flask.wrappers import Response
from werkzeug.wrappers.response import Response as WerkzeugResponse

JSON = Union[dict, list, str, int, float, bool, None]
ResponseValue = Union[Response, WerkzeugResponse, JSON, Tuple[JSON, int], Tuple[Response, int]]
T = TypeVar('T')

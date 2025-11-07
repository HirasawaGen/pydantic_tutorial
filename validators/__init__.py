from .nrange import nrange
from .tensorlike import tensorlike

from functools import wraps
from typing import Callable
from pydantic import validate_call

def hirasawa_validate(func: Callable):
    func.__validate_namespace__: dict = {}  # type: ignore
    @validate_call(validate_return=True, config={'arbitrary_types_allowed': True})
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        func.__validate_namespace__ = {}  # type: ignore
        return res
    return wrapper
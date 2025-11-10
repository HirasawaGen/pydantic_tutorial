from .nrange import nrange
from .tensorshape import tensorshape
from .tensorange import tensorange
from .sympystorage import SympyStorage

from functools import wraps
from typing import Callable
from pydantic import validate_call
from sympy import Expr


def hirasawa_validate(func: Callable):
    func.__validate_equalities__: set[Expr] = set()  # type: ignore
    func.__sympy_storage__ = SympyStorage()  # type: ignore
    func = validate_call(config={'arbitrary_types_allowed': True})(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)  # in order to let finally work.
            func.__validate_equalities__.clear()  # type: ignore
            func.__sympy_storage__.clear()  # type: ignore
            return res
        finally:
            func.__validate_equalities__.clear()  # type: ignore
            func.__sympy_storage__.clear()  # type: ignore
    return wrapper
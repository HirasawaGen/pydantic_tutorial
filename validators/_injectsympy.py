from sympy import Expr
from typing import NoReturn


__all__ = []


class _Expr(Expr):
    def __index__(self) -> NoReturn:
        raise TypeError("This method could not be called, It's just use to lie interpreter.")
    

Expr.__index__ = _Expr.__index__

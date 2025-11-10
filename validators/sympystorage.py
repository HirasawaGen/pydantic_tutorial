import sympy as sp
from sympy import Expr

from functools import singledispatchmethod
from typing import SupportsFloat
from validators._injectsympy import *  # dynanmically inject `__index__` method to sympy Expr

type Number = SupportsFloat


class SympyStorage:
    def __init__(self, threshold: float = 1e-10) -> None:
        self._namespace: dict[str, float] = {}
        self._threshold = threshold
        return super().__init__()
    
    @singledispatchmethod
    def __setitem__(self, key: int | Expr | slice, value: Number) -> None:
        raise TypeError(f"Invalid key type: {type(key).__name__}")
        
    @__setitem__.register
    def _(self, key: int, value: Number) -> None:
        if key == value: return
        raise ValueError(f"Invalid value, {key} != {value}")
        
    @__setitem__.register
    def _(self, key: Expr, value: Number) -> None:
        value = float(value)
        expr = sp.simplify(key - value).subs(self._namespace)
        symbols = expr.free_symbols
        if len(symbols) == 0:
            ans = float(expr)
            if abs(ans) < 1e-10: return
            raise ValueError(f"{key} is already assigned to {value+ans}")
        if len(symbols) == 1:
            symbol = next(iter(symbols))
            if symbol in self._namespace:
                if self._namespace[str(symbol)] == float(expr): return
                raise ValueError(f"{symbol} is already assigned to {self._namespace[str(symbol)]}")
            solve = sp.solve(expr, symbol)
            self._namespace[str(symbol)] = float(solve[0])
        else:
            raise ValueError(f"Error expresion {key} (To many unsolved symbols: {symbols})")
    
    
    @__setitem__.register
    def _(self, key: slice, value: Number) -> None:
        value = float(value)
        start_obj = key.start
        stop_obj = key.stop
        if isinstance(start_obj, Expr):
            expr = sp.simplify(start_obj <= value).subs(self._namespace)
            if len(expr.free_symbols) != 0:
                raise ValueError(f'Unsolved symbols: {expr.free_symbols}')
            if bool(expr) == False:
                raise ValueError(f"Invalid value, value you provide should greater equal than {start_obj}")
        elif start_obj is not None:  # SupportsIndex
            if not start_obj.__index__() <= value:
                raise ValueError("Invalid value, value you provide should greater equal than {start_obj}")
        else:  # None
            if not 0 <= value:
                raise ValueError("Invalid value")
        if isinstance(stop_obj, Expr):
            expr = sp.simplify(value < stop_obj).subs(self._namespace)
            if len(expr.free_symbols) != 0:
                raise ValueError(f'Unsolved symbols: {expr.free_symbols}')
            if bool(expr) == False:
                raise ValueError(f"Invalid value, value you provide should less than {stop_obj}")
        elif stop_obj is not None:  # SupportsIndex
            if not value < stop_obj.__index__():
                raise ValueError(f"Invalid value, value you provide should less than {stop_obj}")
        else:  # None
            pass
        
    @singledispatchmethod
    def __getitem__(self, key: int | Expr | slice) -> Number | bool | None:
        raise TypeError(f"Invalid key type: {type(key).__name__}")
    
    @__getitem__.register
    def _(self, key: int) -> Number:
        return key
    
    @__getitem__.register
    def _(self, key: Expr) -> Number | None:
        ans = sp.simplify(key).subs(self._namespace)
        if not ans.is_number:
            return None
        return float(ans)

    @__getitem__.register
    def _(self, key: slice) -> bool:
        start_obj = key.start
        stop_obj = key.stop
        if stop_obj is None:
            return True
        if isinstance(start_obj, Expr):
            min_val = self[start_obj]
        elif start_obj is None:
            min_val = 0
        else:
            min_val = start_obj.__index__()
        if isinstance(stop_obj, Expr):
            max_val = self[stop_obj]
        else:
            max_val = stop_obj.__index__()
        if min_val is None or max_val is None:
            return True
        min_val = float(min_val)
        max_val = float(max_val)
        return min_val <= max_val
    
    def clear(self) -> None:
        self._namespace.clear()
    

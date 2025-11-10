from pydantic_core import PydanticCustomError
from typing import override, Any

from .base_validators import SubscriptableValidator  # type: ignore


class _NumRangeValidator(SubscriptableValidator):
    def __init__(self, _range: slice):
        self._min_val = float('-inf') if _range.start is None else _range.start
        self._max_val = float('inf') if _range.stop is None else _range.stop
    
    @override
    def validate[T: int | float](self, value: T) -> T:
        if not self._min_val <= value < self._max_val:
            raise PydanticCustomError(
                'interval_error',
                f'This {type(value)} object should be in range [{self._min_val}, {self._max_val}), you provided {value}',
                {'value': value, 'range': (self._min_val, self._max_val)}
            )
        return value
        

nrange = _NumRangeValidator.subscriptable()
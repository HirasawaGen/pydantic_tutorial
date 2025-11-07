from pydantic_core import PydanticCustomError
from typing import override, Any

from .base_validators import SubscriptableValidator  # type: ignore


class _NumRangeValidator(SubscriptableValidator):
    def __init__(self, _range: slice):
        self.min_val = float('-inf') if _range.start is None else _range.start
        self.max_val = float('inf') if _range.stop is None else _range.stop
    
    @override
    def validate[T: int | float](self, value: T) -> T:
        if not self.min_val <= value < self.max_val:
            raise PydanticCustomError(
                'interval_error',
                f'This {type(value)} object should be in range [{self.min_val}, {self.max_val}), you provided {value}',
                {'value': value, 'range': (self.min_val, self.max_val)}
            )
        return value
        

nrange = _NumRangeValidator.subscriptable()
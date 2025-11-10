from typing import override
from pydantic_core import PydanticCustomError

from .base_validators import SubscriptableValidator

from .protocols import TensorProtocol


class _TensorRangeValidator(SubscriptableValidator):
    def __init__(self, _range: slice):
        self._min_val = float('-inf') if _range.start is None else _range.start
        self._max_val = float('inf') if _range.stop is None else _range.stop
        
    @override
    def validate(self, value: TensorProtocol) -> TensorProtocol:
        if value.min() < self._min_val:
            raise PydanticCustomError(
                'tensor-range-error',
                f'This tensor-like object should have a minimum value of {self._min_val}, but its actual minimum value is {value.min()}',
                {'value': f'{type(value).__name__} {value.shape}', 'range': (self._min_val, self._max_val)}
            )
        if value.max() >= self._max_val:
            raise PydanticCustomError(
                'tensor-range-error',
                f'This tensor-like object should have a maximum value of {self._max_val}, but its actual maximum value is {value.max()}',
                {'value': f'{type(value).__name__} {value.shape}', 'range': (self._min_val, self._max_val)}
            )
        return value
    
    
tensorange = _TensorRangeValidator.subscriptable()

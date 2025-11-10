from typing import override, Literal
from pydantic_core import PydanticCustomError
from sympy import Expr
import sympy as sp

from .base_validators import SubscriptableValidator
from .protocols import TensorProtocol
from .sympystorage import SympyStorage
    
    
class _TensorShapeValidator(SubscriptableValidator):
    def __init__(self, size: tuple[int | Literal['*'] | slice | Expr, ...]):
        '''
        int is regular constant size
        slice[int, int] is range
        str is special mark or expression.
        when str is 'a', 'a' will be set to func.__validate_namespace__ as key.
        the value of 'a' is the corresponding size of the tensor.
        slice ':' or string '*' means any size.
        '''
        self._size = size
    
    @override
    def validate(self, value: TensorProtocol) -> TensorProtocol:
        if not isinstance(value, TensorProtocol):
            raise TypeError(f'{self.source_type} is not a tensor-like type')
        if value.ndim != len(self._size):
            raise PydanticCustomError(
                'tensor-shape-mismatch',
                f'This tensor-like object must have {len(self._size)} dimensions, which shape is {value.shape}',
                {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
            )
        sympy_storage: SympyStorage = getattr(self.validate_obj, '__sympy_storage__')
        for i, (required_size, actual_size) in enumerate(zip(self._size, value.shape)):
            if required_size == '*': continue
            try:
                sympy_storage[required_size] = actual_size
            except Exception as e:
                raise PydanticCustomError(
                    'tensor-shape-mismatch',
                    str(e),
                    {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                )
        return value
            
    
    
tensorshape = _TensorShapeValidator.subscriptable()
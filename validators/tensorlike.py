from typing import Protocol, runtime_checkable, Sized, Iterable, override
from pydantic_core import PydanticCustomError

from .base_validators import SubscriptableValidator
from .eval_utils import _safe_eval, _parse_str



@runtime_checkable
class TensorProtocol(Protocol, Sized, Iterable):
    '''
    protocol of numpy.typing.NDArray and torch.tensor etc.
    '''
    @property
    def shape(self) -> tuple[int, ...]: pass
    
    @property
    def ndim(self) -> int: pass
    
    
class _TensorValidator(SubscriptableValidator):
    # TODO: change all the ValueError to PydanticCustomError
    def __init__(self, size: tuple[int | slice | str, ...]):
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
        mapping = self.namespace
        if value.ndim != len(self._size):
            raise PydanticCustomError(
                'tensor-dimensions-mismatch',
                f'This tensor-like object must have {len(self._size)} dimensions, which shape is {value.shape}',
                {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
            )
        for i, (required_size, actual_size) in enumerate(zip(self._size, value.shape)):
            if required_size == '*': continue
            if isinstance(required_size, int):
                if required_size == actual_size: continue
                # mat = TensorValidator[2, 2]  # in class definition
                # self.mat = np.zeros((3, 2))  # error
                raise PydanticCustomError(
                    'tensor-dimension-size-mismatch',
                    f'The {i}-th dimension of this tensor-like object must have size {required_size}, you provide {actual_size}',
                    {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                )
            elif isinstance(required_size, slice):
                if required_size.start is None and required_size.stop is None and required_size.step is None:
                    # mat = TensorValidator[:, 2], ':' means any size on 0-th dimension.
                    continue
                min_size = required_size.start or 0
                max_size = required_size.stop or float('inf')
                if required_size.step is not None:
                    '''
                    mat = TensorValidator[0::2]
                    self.mat = np.zeros((0, 2))  # right
                    self.mat = np.zeros((1, 2))  # error
                    self.mat = np.zeros((2, 2))  # right
                    self.mat = np.zeros((3, 2))  # error
                    '''
                    ...  # TODO: step is not supported yet.
                if min_size <= actual_size < max_size: continue
                # mat = TensorValidator[3:5, 2]
                # self.mat = np.zeros((2, 2))  # error
                raise PydanticCustomError(
                    'tensor-dimension-size-mismatch',
                    f'The {i}-th dimension of this tensor-like object must have size in range [{min_size}, {max_size}), you provide {actual_size}',
                    {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                )
            elif isinstance(required_size, str):
                
                if ':' in required_size:
                    if required_size.count(':') != 1:
                        # mat = TensorValidator['a:b:30', 2]  # error
                        raise PydanticCustomError(
                            'range-expression-syntax-error',
                            f'string size must have only one ":", walrus operator and typehints is not allowed.',
                            {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                        )
                    splits = required_size.split(':')
                    min_size = _parse_str(splits[0], mapping=mapping, actual_size=actual_size) if splits[0] else 0
                    max_size = _parse_str(splits[1], mapping=mapping, actual_size=actual_size) if splits[1] else float('inf')
                    if max_size < min_size:
                        raise PydanticCustomError(
                            'range-expression-syntax-error',
                            f'string size must have only one ":", walrus operator and typehints is not allowed.',
                            {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                        )
                    if min_size <= actual_size < max_size: continue
                    # raise ValueError(f'the {i}-th dimension of this tensor-like object must have size in range [{min_size}, {max_size})')
                    raise PydanticCustomError(
                        'tensor-dimension-size-mismatch',
                        f'The {i}-th dimension of this tensor-like object must have size in range [{min_size}, {max_size}), you provide {actual_size}',
                        {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                    )
                required_size_int = _parse_str(required_size, mapping=mapping, actual_size=actual_size)
                if actual_size == required_size_int: continue
                raise PydanticCustomError(
                    'tensor-dimension-size-mismatch',
                    f'The {i}-th dimension of this tensor-like object must have size {required_size_int}, (symbol "{required_size}"), you provide {actual_size}',
                    {'value': f'{type(value).__name__} {value.shape}', 'size': self._size}
                )
            else:
                raise TypeError(f'this tensor-like object size must be int or slice or str, got {required_size} at {i}-th dimension.')
        return value
            
    
    
tensorlike = _TensorValidator.subscriptable()
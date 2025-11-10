from functools import wraps
from pytest import mark
import pytest

from pydantic import ValidationError

from typing import Annotated as Annt

import numpy as np
from numpy.typing import NDArray

from sympy.abc import X, Y, Z, W, H

from validators import tensorshape
from validators import hirasawa_validate


def should_raise(*exceptions: type[Exception]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with pytest.raises(exceptions) as exception_info:
                func(*args, **kwargs)
            print(f'\n{exception_info.value}')
        return wrapper
    return decorator


# NDArray[np.float64] is a type hint for numpy array with float64 data type
arr: NDArray[np.float64] = np.random.rand(3, 4)

# Annotated is a type hint for a type with metadata
num: Annt[int, 'some metadata'] = 5


@hirasawa_validate
def func1(
    mat1: Annt[NDArray[np.float64],
        tensorshape[2*W, 2*H],
    ],
    mat2: Annt[NDArray[np.float64],
        tensorshape[H, W],
    ],
):
    # width of mat1 must be twice the width of mat2
    # height of mat1 must be twice the height of mat2
    # automically validated by pydantic
    w, h = mat1.shape
    mat1 = mat1[:w, :h]
    return mat1 @ mat2


@mark.parametrize('shapes', [
    [(4, 6), (6, 4)],  # The 0-th dimension of this tensor-like object must have size 3 (symbol "H"), you provide 6
    [(2, 8), (4, 2)],  # The 1-th dimension of this tensor-like object must have size 2 (symbol "W"), you provide 1
])
@should_raise(ValidationError)
def test_func1(shapes):
    mat0 = np.random.rand(*shapes[0])
    mat1 = np.random.rand(*shapes[1])
    func1(mat0, mat1)

    
@hirasawa_validate
def func2(
    mat: Annt[NDArray[np.float64], tensorshape[9, 9],]
):
    # width of mat must be in range [0, 9)
    # height of mat must be in range [9, +inf)
    # automically validated by pydantic
    pass


@should_raise(ValidationError)
def test_func2():
    # The 0-th dimension of this tensor-like object must have size in range [0, 9), you provide 10
    mat = np.random.rand(1, 81)
    mat = mat.reshape(9, 9)
    func2(mat)

    
@hirasawa_validate
def func3(
    data1: Annt[NDArray[np.float64],
        tensorshape['*', X, Y-1],
    ],
    data2: Annt[NDArray[np.float64],
        tensorshape[X:, X+2, X:Y],
    ],
):
    # no constraint on data1
    # 0-th dimension of data2 must be in range [X, +inf)
    # 1-th dimension of data2 must be X+2
    # 2-th dimension of data2 must be in range [X, Y)
    # automically validated by pydantic
    pass


@mark.parametrize('shapes', [
    [(1, 4, 6), (1, 6, 5)],  # The 0-th dimension of this tensor-like object must have size in range [4, inf), you provide 1
    [(2, 4, 6), (4, 7, 5)],  # The 1-th dimension of this tensor-like object must have size 6 (symbol "X + 2"), you provide 7
    [(3, 4, 6), (4, 6, 9)],  # The 2-th dimension of this tensor-like object must have size in range [4， 7), you provide 9
])
@should_raise(ValidationError)
def test_func3(shapes):
    data0 = np.random.rand(*shapes[0])
    data1 = np.random.rand(*shapes[1])
    print()
    print(f'{data0.shape=}')
    print(f'{data1.shape=}')
    func3(data0, data1)


    




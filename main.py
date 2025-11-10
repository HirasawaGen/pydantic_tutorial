from typing import Annotated as Annt

import numpy as np
from numpy.typing import NDArray

from validators import tensorshape
from validators import hirasawa_validate

from sympy.abc import X, Y


@hirasawa_validate
def func(
    data1: Annt[NDArray[np.float64],
        tensorshape['*', X, Y],
    ],
    data2: Annt[NDArray[np.float64],
        tensorshape[X:, X+2, X:Y],
    ],
):
    # no constraint on data1
    # '*' means any number of dimensions
    # 0-th dimension of data2 must be in range [X, +inf)
    # 1-th dimension of data2 must be X+2
    # 2-th dimension of data2 must be in range [X, Y)
    # automically validated by pydantic
    pass


data1 = np.random.rand(1, 4, 6)
data2 = np.random.rand(1, 6, 5)
try:
    func(data1, data2)
except Exception as e:
    print(e)
    # The 0-th dimension of this tensor-like object must have size in range [4, inf), you provide 1

data1 = np.random.rand(2, 4, 6)
data2 = np.random.rand(4, 7, 5)
try:
    func(data1, data2)
except Exception as e:
    print(e)
    # The 1-th dimension of this tensor-like object must have size 6 (symbol "X + 2"), you provide 7

data1 = np.random.rand(3, 4, 6)
data2 = np.random.rand(4, 6, 9)
try:
    func(data1, data2)
except Exception as e:
    print(e)
    # The 2-th dimension of this tensor-like object must have size in range [X, Y), you provide 9
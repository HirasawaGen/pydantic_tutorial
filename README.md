## Constraint Tensor Size by Integer

```python
from typing import Annotated as Annt

import numpy as np
from numpy.typing import NDArray

from validators import tensorshape
from validators import hirasawa_validate


@hirasawa_validate
def func(
    mat: Annt[NDArray[np.float64], tensorshape[:9, 9:],]
):
    # width of mat must be in range [0, 9)
    # height of mat must be in range [9, +inf)
    # automically validated by pydantic
    pass

mat = np.random.rand(10, 10)
func(mat)
# Output: The 0-th dimension of this tensor-like object must have size in range [0, 9), you provide 10
```

# Constraint Tensor Size by Sympy

```python
from typing import Annotated as Annt

import numpy as np
from numpy.typing import NDArray

from validators import tensorshape
from validators import hirasawa_validate

from sympy.abc import W, H


@hirasawa_validate
def func(
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

mat1 = np.random.rand(6, 8)
mat2 = np.random.rand(8, 6)
# you forgot mat1 will be cliped. So you input 'correct' size of mat1
func(mat1, mat2)
# The 0-th dimension of this tensor-like object must have size 4 (symbol "H"), you provide 8
```


# Constraint Tensor Size on Extremely Complex Conditions

```python
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
    # The 2-th dimension of this tensor-like object must have size in range [4, 6), you provide 9
```


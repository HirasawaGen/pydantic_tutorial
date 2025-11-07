from typing import Annotated as Annot

import numpy as np
from numpy.typing import NDArray

from validators import nrange
from validators import tensorlike
from validators import hirasawa_validate


@hirasawa_validate
def multiply_mat(
    mat1: Annot[
        NDArray[np.float64],
        tensorlike[:8, 'b']
    ],
    mat2: Annot[
        NDArray[np.float64],
        tensorlike['b', :8]
    ],
) -> NDArray[np.float64]:
    return mat1 @ mat2



try:
    mat1 = np.random.rand(5, 4)
    mat2 = np.random.rand(5, 5)
    print(multiply_mat(mat1, mat2).shape)
except Exception as e:
    print(e)
    '''
    终端输出：
    The 0-th dimension of this tensor-like object must have size 4, (symbol "b"), you provide 5
    '''
    
    
try:
    mat1 = np.random.rand(5, 4)
    mat2 = np.random.rand(4, 9)
    print(multiply_mat(mat1, mat2).shape)
except Exception as e:
    print(e)
    '''
    终端输出：
    The 0-th dimension of this tensor-like object must have size 4, (symbol "b"), you provide 5
    '''

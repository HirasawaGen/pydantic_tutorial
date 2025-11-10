from __future__ import annotations

from typing import Protocol, runtime_checkable, Sized, Iterable, SupportsIndex, Sequence

from numpy import ndarray


@runtime_checkable
class TensorProtocol[DType](Protocol, Sized, Iterable):
    '''
    protocol of numpy.typing.NDArray and torch.tensor etc.
    '''
    @property
    def dtype(self) -> type[DType]: pass
    
    @property
    def shape(self) -> tuple[int, ...]: pass
    
    @property
    def ndim(self) -> int: pass
    
    def min(
        self,
        /,
        axis: SupportsIndex | Sequence[SupportsIndex] | None = None,
        **kwargs
    ) -> DType | ndarray: pass
    
    def max(
        self,
        /,
        axis: SupportsIndex | Sequence[SupportsIndex] | None = None,
        **kwargs
    ) -> DType | ndarray: pass
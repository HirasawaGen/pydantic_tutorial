from abc import ABC, abstractmethod
from typing import Callable, Any

from pydantic_core import core_schema

from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler
from functools import lru_cache


class BaseValidator(ABC):
    source_type: type
    validate_obj: Any
    symbol_namespace: dict[str, Any]
    
    @abstractmethod
    def validate(self, value: Any) -> Any:
        pass
    
    def __get_pydantic_core_schema__(
        self,
        source_type: type,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        locals_namespace = getattr(handler._get_types_namespace().locals, 'data', {})
        global_namespace = handler._get_types_namespace().globals
        decorated_func = locals_namespace.get('func')
        self.source_type = source_type
        self.validate_obj = decorated_func
        def function(value: Any, handler: Callable):
            return self.validate(value)
        return core_schema.no_info_wrap_validator_function(
            function,
            handler(source_type),
        )
        

class SubscriptableValidator(BaseValidator):
    @classmethod
    @lru_cache(maxsize=1)
    def subscriptable(cls):
        class Subscriptable:
            def __getitem__(self, *args, **kwargs):
                return cls(*args, **kwargs)
        return Subscriptable()
    


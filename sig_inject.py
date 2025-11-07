from inspect import signature,  Parameter, Signature, _empty, _ParameterKind
from functools import wraps
from pydantic import validate_call


# def str2param(param_str: str) -> Parameter:
#     mapping: dict = {}
#     exec(f'def f({param_str}): ...', globals(), mapping)
#     dummy = mapping['f']
#     @wraps(dummy)
#     def _(): ...
#     sig = signature(_)
#     return sig.parameters[list(sig.parameters.keys())[0]]



def sig_inject(params: list[str | tuple], ret: type, /):
    updated_params: list[Parameter] = []
    __annotations__: dict = {}
    has_star: bool = False  # whether there is a `*` parameter
    for param in params:
        if param == '*':
            has_star = True
            continue
        if param == '/':
            for i in range(len(updated_params)):
                updated_params[i] = updated_params[i].replace(kind=Parameter.POSITIONAL_ONLY)
            continue
        if isinstance(param, str):
            name = param
            annotation = _empty
            default = _empty
        elif isinstance(param, tuple):
            if len(param) == 2:
                name, annotation = param
                default = _empty
            elif len(param) == 3:
                name, annotation, default = param
                if annotation == '':
                    annotation = _empty
        else:
            raise TypeError(f'Invalid parameter: {param}')
        kind: _ParameterKind = Parameter.POSITIONAL_OR_KEYWORD if not has_star else Parameter.KEYWORD_ONLY
        if name.startswith('**'):
            name = name[2:]
            kind = Parameter.VAR_KEYWORD
        elif name.startswith('*'):
            name = name[1:]
            kind = Parameter.VAR_POSITIONAL
        updated_params.append(Parameter(name, kind, default=default, annotation=annotation))
        __annotations__[name] = annotation
    sig = Signature(parameters=updated_params, return_annotation=ret)
    def decorator(func):
        func.__signature__ = sig  # type: ignore
        func.__annotations__ = __annotations__  # type: ignore
        return func
    return decorator


@validate_call
@sig_inject(
    [
        '*args',
        '**kwargs'
    ], int
)
def my_func(a, b):
    print(a, b)
    return 0


print(signature(my_func))
print(my_func(1, 2))

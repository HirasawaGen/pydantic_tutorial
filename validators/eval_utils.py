import ast
from typing import Any


def _safe_eval(expr, globals: dict | None = None, locals: dict | None = None) -> Any:
    # 解析表达式为语法树
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError("Invalid expression syntax")
    
    # 检查所有节点是否合法（只允许操作符和字面量）
    allowed_nodes = (
        ast.Name,        # 变量名
        ast.Load,        # 变量加载
        ast.Expression,  # 根节点
        ast.BinOp,       # 二元操作符（+、-、*等）
        ast.UnaryOp,     # 一元操作符（-、+等）
        ast.Constant,    # 字面量（数字、字符串等，Python 3.8+）
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,  # 二元操作符类型
    )
    
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Invalid element in expression: {type(node).__name__}")
    
    # 安全执行合法表达式
    return eval(compile(tree, '<string>', 'eval'), globals, locals)


def _parse_str(expr: str, mapping: dict, actual_size: int) -> int:
    if expr.isdigit():
        return int(expr)
    elif expr.isidentifier():
        if expr not in mapping:
            mapping[expr] = actual_size
        return mapping[expr]
    else:
        try:
            return int(_safe_eval(expr, {}, mapping))
        except NameError:
            # mat_1 = TensorValidator['a', 'a+1']  # right
            # mat_2 = TensorValidator['b+1', 'b']  # error
            raise ValueError(f'String size must be a single string when they first used.')
        except TypeError:
            # mat = TensorValidator['a', 'a+1.23']   # error
            raise ValueError(f'Expression must return an integer.')
        except SyntaxError:
            # mat = TensorValidator['a', 3, 4:7, 'a++']  # error
            raise ValueError(f'Invalid size expression: {expr}')
        except Exception as e:
            # I don't know what other exception can be raised here.
            print(e)
            raise ValueError(f'Invalid size expression: {expr}')
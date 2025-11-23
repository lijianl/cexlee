from typing import Callable, Any, Optional, List, Dict, Union, Awaitable
from functools import wraps
from kitx.LogUtil import LogUtil
import uuid

logger = LogUtil.get_logger2("FuncUtil")


class FuncUtil:

    def log_func_proxy(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{func.__name__} request: args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} response: {result}")
            return result

        return wrapper

    def log_func_annotation(self, traceId: str):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"{func.__name__} req: args={args}, kwargs={kwargs}; reqId={traceId} ")
                return func(*args, **kwargs)

            return wrapper

        # 返回decorator
        return decorator


def run1():
    def hello(name: str, **kwargs):
        return f"hello,{name}"

    hellop = FuncUtil.log_func_proxy(None, hello)
    hellop("1111", k1="v1")


def run2():
    @FuncUtil.log_func_annotation(None, uuid.uuid4().hex)
    def hello(name: str, **kwargs):
        return f"hello,{name}"

    hello("2222", k1="v2")


if __name__ == '__main__':
    run1()
    run2()

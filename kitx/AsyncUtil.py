import asyncio
import concurrent.futures
from typing import Callable, Any, List, Optional
import threading
from kitx.LogUtil import LogUtil

logger = LogUtil.get_logger2("AsyncUtil")


class AsyncUtil:

    def __init__(self):
        """public属性"""
        self.loop = None
        self.executor = None
        """private method"""
        self._setup_event_loop()

    def _setup_event_loop(self):
        """设置事件循环"""
        try:
            # 尝试获取: 当前线程的事件循环
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            # 如果没有运行中的事件循环，则创建一个新的
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # 创建线程池执行器用于运行同步函数
        self.executor = concurrent.futures.ThreadPoolExecutor()

    async def run_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        异步执行函数

        Args:
            func: 要执行的函数，支持函数，coroutine
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数

        Returns:
            函数执行结果
        """
        if asyncio.iscoroutinefunction(func):
            # 如果是异步函数，直接await, 协程
            return await func(*args, **kwargs)
        else:
            # 如果是同步函数，在线程池中执行
            return await self.loop.run_in_executor(
                self.executor,
                lambda: func(*args, **kwargs)
            )

    async def run_multiple_async(self, funcs: List[tuple]) -> List[Any]:
        """
        并发执行多个函数

        Args:
            funcs: 函数元组列表，每个元组格式为 (func, args, kwargs) 或 (func, args) 或 (func,)

        Returns:
            所有函数执行结果的列表
        """
        tasks = []
        for func_item in funcs:
            if isinstance(func_item, tuple):
                # 获取函数的参数
                func = func_item[0]
                args = func_item[1] if len(func_item) > 1 else ()
                kwargs = func_item[2] if len(func_item) > 2 else {}
                tasks.append(self.run_async(func, *args, **kwargs))
            else:
                # 如果直接传入函数
                tasks.append(self.run_async(func_item))

        return await asyncio.gather(*tasks)

    def run_sync(self, coro) -> Any:
        """
        在同步上下文中运行异步函数

        Args:
            coro: 异步函数或协程对象

        Returns:
            异步函数执行结果
        """
        if asyncio.iscoroutine(coro):
            # 如果是协程对象
            return self.loop.run_until_complete(coro)
        elif asyncio.iscoroutinefunction(coro):
            # 如果是异步函数
            return self.loop.run_until_complete(coro())
        else:
            return coro

    async def run_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        """
        带超时控制的异步执行函数

        Args:
            func: 要执行的函数
            timeout: 超时时间（秒）
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数

        Returns:
            函数执行结果

        Raises:
            asyncio.TimeoutError: 如果函数执行超时
        """
        try:
            return await asyncio.wait_for(self.run_async(func, *args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Function {func.__name__} execution timed out after {timeout} seconds")

    def close(self):
        """关闭线程池资源"""
        if self.executor:
            self.executor.shutdown(wait=True)

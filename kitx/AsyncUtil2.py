import asyncio
import concurrent.futures
from typing import Callable, Any, Optional, List, Dict, Union, Awaitable
from functools import wraps
import time
from datetime import datetime
from kitx.LogUtil import LogUtil

logger = LogUtil.get_logger2("AsyncUtil")


class AsyncUtil2:
    """
    异步执行工具类
    """
    def __init__(self, max_workers: int = 10, thread_pool: bool = True):
        """
        初始化异步工具类
        """
        self.max_workers = max_workers
        self.thread_pool = thread_pool
        self._executor = None
        self._loop = None
        self._tasks = {}

        #  创建执行器
        if thread_pool:
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        else:
            self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)

    def __del__(self):
        """析构函数，清理资源"""
        if self._executor:
            self._executor.shutdown(wait=True)

    def close(self):
        """关闭执行器"""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

    async def run_async(self, func: Callable, *args, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        task_id = f"{func.__name__}_{id(func)}_{time.time()}"

        logger.info(f"开始异步执行任务:  {task_id}")
        start_time = time.time()

        try:
            #  在线程池中执行函数
            result = await loop.run_in_executor(
                self._executor,
                # 函数wrapper
                self._wrap_function(func, task_id),
                *args,
                **kwargs
            )
            elapsed = time.time() - start_time
            logger.info(f"异步任务  {task_id}  执行完成，耗时:  {elapsed:.2f}秒")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"异步任务  {task_id}  执行失败，耗时:  {elapsed:.2f}秒，错误:  {e}")
            raise

    async def run_multiple(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        if not tasks:
            return []

        logger.info(f"开始并发执行  {len(tasks)}  个异步任务")
        start_time = time.time()
        try:
            coroutines = []
            for i, task in enumerate(tasks):
                # [()]
                func = task['func']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                coro = self.run_async(func, *args, **kwargs)
                coroutines.append(coro)

            #  并发执行所有任务
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            elapsed = time.time() - start_time
            logger.info(f"所有异步任务执行完成，总耗时:  {elapsed:.2f}秒")

            #  处理异常结果
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"任务  {i}  执行失败:  {result}")
                    final_results.append(None)
                else:
                    final_results.append(result)
            return final_results

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"并发执行任务失败，耗时:  {elapsed:.2f}秒，错误:  {e}")
            raise

    async def run_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        logger.info(f"开始执行带超时的任务:  {func.__name__}，超时时间:  {timeout}秒")
        try:
            result = await asyncio.wait_for(
                self.run_async(func, *args, **kwargs),
                timeout=timeout
            )
            logger.info(f"带超时任务执行成功:  {func.__name__}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"任务执行超时:  {func.__name__}，超时时间:  {timeout}秒")
            raise

    async def retry_async(self, func: Callable, max_retries: int = 3,
                          delay: float = 1.0, backoff: float = 2.0,
                          *args, **kwargs) -> Any:
        """
        带重试机制的异步执行

        Args:
            func:  要执行的函数
            max_retries:  最大重试次数
            delay:  初始延迟时间（秒）
            backoff:  延迟时间的增长因子
            *args:  函数位置参数
            **kwargs:  函数关键字参数
         """
        logger.info(f"开始执行带重试的任务:  {func.__name__}，最大重试次数:  {max_retries}")
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"第  {attempt + 1}  次尝试执行任务:  {func.__name__}")
                result = await self.run_async(func, *args, **kwargs)
                logger.info(f"任务执行成功:  {func.__name__}，尝试次数:  {attempt + 1}")
                return result
            except Exception as e:
                if attempt < max_retries:
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"任务执行失败:  {func.__name__}，错误:  {e}，{wait_time}秒后重试")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"任务执行失败，已达到最大重试次数:  {func.__name__}，错误:  {e}")
                raise

    def _wrap_function(self, func: Callable, task_id: str) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"任务  {task_id}  开始执行函数:  {func.__name__}")
                result = func(*args, **kwargs)
                logger.debug(f"任务  {task_id}  函数执行完成:  {func.__name__}")
                return result
            except  Exception as e:
                logger.error(f"任务  {task_id}  函数执行失败:  {func.__name__},  错误:  {e}")
                raise

        return wrapper

    def async_decorator(self, timeout: Optional[float] = None, max_retries: int = 0):
        """
        异步执行装饰器
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if max_retries > 0:
                    coro = self.retry_async(func, max_retries, *args, **kwargs)
                else:
                    coro = self.run_async(func, *args, **kwargs)
                if timeout:
                    coro = self.run_with_timeout(func, timeout, *args, **kwargs)
                return self.run_sync(coro)
            return wrapper

        return decorator

    def run_sync(self, coro: Awaitable) -> Any:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("事件循环已关闭")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"同步运行异步协程失败:  {e}")
            raise


#  使用示例和测试代码
if __name__ == "__main__":
    #  创建异步工具实例
    async_util = AsyncUtil2(max_workers=5)

    def slow_function(name: str, delay: float = 1.0):
        """模拟耗时函数"""
        print(f"[{datetime.now()}]  开始执行函数:  {name}，延迟:  {delay}秒")
        time.sleep(delay)
        print(f"[{datetime.now()}]  函数执行完成:  {name}")
        return f"结果:  {name}  -  {delay}"


    def failing_function():
        """模拟失败函数"""
        print(f"[{datetime.now()}]  执行失败函数")
        raise ValueError("模拟函数执行失败")


    #  示例1:  基本异步执行
    async def demo_basic():
        print("===  基本异步执行示例  ===")
        result = await  async_util.run_async(slow_function, "任务1", 1.0)
        print(f"异步执行结果:  {result}")


    #  示例2:  并发执行多个任务
    async def demo_multiple():
        print("\n===  并发执行多个任务示例  ===")
        tasks = [
            {'func': slow_function, 'args': ("任务A", 1.0)},
            {'func': slow_function, 'args': ("任务B", 2.0)},
            {'func': slow_function, 'args': ("任务C", 1.5)},
        ]
        results = await async_util.run_multiple(tasks)
        print(f"并发执行结果:  {results}")


    #  示例3:  带超时的异步执行
    async def demo_timeout():
        print("\n===  带超时的异步执行示例  ===")
        try:
            result = await async_util.run_with_timeout(slow_function, 1.5, "超时任务", 1.0)
            print(f"超时执行结果:  {result}")
        except  asyncio.TimeoutError:
            print("任务执行超时")


    #  示例4:  带重试的异步执行
    async def demo_retry():
        print("\n===  带重试的异步执行示例  ===")
        try:
            result = await async_util.retry_async(failing_function, max_retries=2, delay=0.5)
            print(f"重试执行结果:  {result}")
        except  Exception as e:
            print(f"重试后仍然失败:  {e}")


    #  示例5:  装饰器使用
    def demo_decorator():
        print("\n===  装饰器使用示例  ===")

        #  使用装饰器
        @async_util.async_decorator(timeout=2.0, max_retries=1)
        def decorated_function(name: str):
            return slow_function(f"装饰器_{name}", 0.5)

        result = decorated_function("测试")
        print(f"装饰器执行结果:  {result}")


    #  运行所有示例
    async def run_all_demos():
        await demo_basic()
        await demo_multiple()
        await demo_timeout()
        await demo_retry()

        #  装饰器示例在同步上下文中运行
        demo_decorator()


#  主函数
def main():
    print("开始异步工具类演示...")
    start_time = time.time()

    #  运行异步演示
    async_util.run_sync(run_all_demos())

    elapsed = time.time() - start_time
    print(f"\n所有演示完成，总耗时:  {elapsed:.2f}秒")

    #  关闭资源
    async_util.close()
    print("异步工具类演示结束!")


#  运行主函数
main()

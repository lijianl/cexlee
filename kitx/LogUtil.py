import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class LogUtil:
    """
    静态日志工厂类
    """

    _default_log_dir = Path(__file__).parent.parent / 'logs'
    _default_level = logging.DEBUG
    _default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    _default_date_format = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def get_logger(name: str, log_file: Optional[str] = None, level: int = None, log_dir: str = None,
                   enable_console: bool = True,
                   enable_file: bool = True,
                   max_bytes: int = 10 * 1024 * 1024,
                   backup_count: int = 5) -> logging.Logger:
        """
        静态方法：获取或创建logger实例
        
        Args:
            name: logger名称
            log_file: 日志文件名，如果为None则使用name参数
            level: 日志级别，如果为None则使用默认级别
            log_dir: 日志目录，如果为None则使用默认目录
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 备份文件数量
            
        Returns:
            logging.Logger: 配置好的logger实例
        """

        # 使用默认参数
        if level is None:
            level = LogUtil._default_level
        if log_dir is None:
            log_dir = LogUtil._default_log_dir
        if log_file is None:
            log_file = f"{name}.log"

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 创建logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 创建格式器
        formatter = logging.Formatter(
            LogUtil._default_format,
            datefmt=LogUtil._default_date_format
        )

        # 文件处理器
        if enable_file:
            try:
                from logging.handlers import RotatingFileHandler
                log_path = os.path.join(log_dir, log_file)
                file_handler = RotatingFileHandler(
                    log_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"创建文件日志处理器失败: {e}")

        # 控制台处理器
        if enable_console:
            try:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(level)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
            except Exception as e:
                print(f"创建控制台日志处理器失败: {e}")
        return logger

    @staticmethod
    def set_default_config(log_dir: str = None, level: int = None,
                           format_str: str = None, date_format: str = None):
        """
        静态方法：设置默认日志配置

        Args:
            log_dir: 默认日志目录
            level: 默认日志级别
            format_str: 默认日志格式
            date_format: 默认日期格式
        """
        if log_dir is not None:
            LogUtil._default_log_dir = log_dir
        if level is not None:
            LogUtil._default_level = level
        if format_str is not None:
            LogUtil._default_format = format_str
        if date_format is not None:
            LogUtil._default_date_format = date_format

    @staticmethod
    def get_logger2(name: str, log_dir: str = None) -> logging.Logger:
        return LogUtil.get_logger_with_date(name, logging.DEBUG, log_dir=LogUtil._default_log_dir)

    @staticmethod
    def get_logger_with_date(name: str, level: int = None, log_dir: str = None,
                             enable_console: bool = True, enable_file: bool = True) -> logging.Logger:

        """
        静态方法：获取带日期后缀的logger

        Args:
            name: logger名称
            level: 日志级别
            log_dir: 日志目录
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出

        Returns:
            logging.Logger: 配置好的logger实例
        """
        log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        return LogUtil.get_logger(
            name=name,
            log_file=log_file,
            level=level,
            log_dir=log_dir,
            enable_console=enable_console,
            enable_file=enable_file
        )


if __name__ == '__main__':
    logger = LogUtil.get_logger2("LogUtil")
    logger.debug("这是一条debug日志")
    logger.info("这是一条info日志")
    logger.warning("这是一条warning日志")
    logger.error("这是一条error日志")
    logger.critical("这是一条critical日志")

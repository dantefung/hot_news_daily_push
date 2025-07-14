#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理器模块 - 包含扩展点接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PostProcessorInterface(ABC):
    """
    后置处理器接口 - 用户可以实现此接口来扩展处理能力
    """

    @abstractmethod
    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容

        Args:
            summary: 原始摘要内容
            context: 处理上下文，包含各种配置和数据

        Returns:
            str: 处理后的摘要内容
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        获取处理器名称

        Returns:
            str: 处理器名称
        """
        pass

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """
        检查处理器是否启用

        Args:
            context: 处理上下文

        Returns:
            bool: 是否启用
        """
        return True

    def get_priority(self) -> int:
        """
        获取处理器优先级（数字越小优先级越高）

        Returns:
            int: 优先级
        """
        return 100


class ProcessorManager:
    """
    处理器管理器 - 管理所有注册的后置处理器
    """

    def __init__(self):
        self.processors = []

    def register_processor(self, processor: PostProcessorInterface):
        """
        注册后置处理器

        Args:
            processor: 后置处理器实例
        """
        self.processors.append(processor)
        logger.info(f"注册后置处理器: {processor.get_name()}")

    def process_summary(self, summary: str, context: Dict[str, Any]) -> str:
        """
        按优先级顺序执行所有启用的后置处理器

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 最终处理后的摘要内容
        """
        # 按优先级排序
        enabled_processors = [
            p for p in self.processors
            if p.is_enabled(context)
        ]
        enabled_processors.sort(key=lambda p: p.get_priority())

        current_summary = summary

        for processor in enabled_processors:
            try:
                logger.info(f"执行后置处理器: {processor.get_name()}")
                current_summary = processor.process(current_summary, context)
                logger.info(f"后置处理器 {processor.get_name()} 执行完成")
            except Exception as e:
                logger.error(f"后置处理器 {processor.get_name()} 执行失败: {e}")
                # 继续执行下一个处理器，不中断流程

        return current_summary


# 全局处理器管理器实例
processor_manager = ProcessorManager()


def register_post_processor(processor: PostProcessorInterface):
    """
    注册后置处理器的便捷函数

    Args:
        processor: 后置处理器实例
    """
    processor_manager.register_processor(processor)


def process_summary_with_plugins(summary: str, context: Dict[str, Any]) -> str:
    """
    使用所有注册的插件处理摘要

    Args:
        summary: 原始摘要内容
        context: 处理上下文

    Returns:
        str: 处理后的摘要内容
    """
    return processor_manager.process_summary(summary, context)

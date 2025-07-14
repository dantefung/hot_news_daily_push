#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试扩展点系统
"""

import unittest
from unittest.mock import Mock, patch
from processor import PostProcessorInterface, ProcessorManager, register_post_processor, process_summary_with_plugins
from typing import Dict, Any


class MockProcessor(PostProcessorInterface):
    """模拟处理器用于测试"""

    def __init__(self, name="MockProcessor", priority=100, enabled=True, return_value=None):
        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.return_value = return_value
        self.process_called = False

    def get_name(self) -> str:
        return self.name

    def get_priority(self) -> int:
        return self.priority

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        return self.enabled

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        self.process_called = True
        return self.return_value if self.return_value else summary


class TestExtensionSystem(unittest.TestCase):
    """测试扩展点系统"""

    def setUp(self):
        """测试前准备"""
        self.manager = ProcessorManager()
        self.test_summary = "测试摘要内容"
        self.test_context = {"test_key": "test_value"}

    def test_processor_registration(self):
        """测试处理器注册"""
        processor = MockProcessor("TestProcessor")
        self.manager.register_processor(processor)

        self.assertEqual(len(self.manager.processors), 1)
        self.assertEqual(self.manager.processors[0], processor)

    def test_processor_priority_sorting(self):
        """测试处理器优先级排序"""
        processor1 = MockProcessor("Processor1", priority=50)
        processor2 = MockProcessor("Processor2", priority=10)
        processor3 = MockProcessor("Processor3", priority=100)

        self.manager.register_processor(processor1)
        self.manager.register_processor(processor2)
        self.manager.register_processor(processor3)

        # 按优先级排序
        enabled_processors = [
            p for p in self.manager.processors if p.is_enabled(self.test_context)]
        enabled_processors.sort(key=lambda p: p.get_priority())

        self.assertEqual(
            enabled_processors[0].get_name(), "Processor2")  # 优先级最高
        self.assertEqual(enabled_processors[1].get_name(), "Processor1")
        self.assertEqual(
            enabled_processors[2].get_name(), "Processor3")  # 优先级最低

    def test_processor_execution(self):
        """测试处理器执行"""
        processor1 = MockProcessor(
            "Processor1", priority=10, return_value="处理后的摘要1")
        processor2 = MockProcessor(
            "Processor2", priority=20, return_value="处理后的摘要2")

        self.manager.register_processor(processor1)
        self.manager.register_processor(processor2)

        result = self.manager.process_summary(
            self.test_summary, self.test_context)

        # 验证处理器被调用
        self.assertTrue(processor1.process_called)
        self.assertTrue(processor2.process_called)

        # 验证最终结果（应该是最后一个处理器的输出）
        self.assertEqual(result, "处理后的摘要2")

    def test_processor_disabled(self):
        """测试禁用处理器"""
        enabled_processor = MockProcessor("EnabledProcessor", enabled=True)
        disabled_processor = MockProcessor("DisabledProcessor", enabled=False)

        self.manager.register_processor(enabled_processor)
        self.manager.register_processor(disabled_processor)

        result = self.manager.process_summary(
            self.test_summary, self.test_context)

        # 只有启用的处理器被调用
        self.assertTrue(enabled_processor.process_called)
        self.assertFalse(disabled_processor.process_called)

    def test_processor_error_handling(self):
        """测试处理器错误处理"""
        def failing_process(summary, context):
            raise Exception("处理器错误")

        error_processor = MockProcessor("ErrorProcessor")
        error_processor.process = failing_process

        normal_processor = MockProcessor(
            "NormalProcessor", return_value="正常处理")

        self.manager.register_processor(error_processor)
        self.manager.register_processor(normal_processor)

        # 即使有错误，其他处理器仍应继续执行
        result = self.manager.process_summary(
            self.test_summary, self.test_context)

        self.assertEqual(result, "正常处理")

    def test_global_functions(self):
        """测试全局函数"""
        processor = MockProcessor("TestProcessor", return_value="处理后的摘要")

        # 测试注册函数
        register_post_processor(processor)

        # 测试处理函数
        result = process_summary_with_plugins(
            self.test_summary, self.test_context)

        self.assertTrue(processor.process_called)
        self.assertEqual(result, "处理后的摘要")


if __name__ == "__main__":
    unittest.main()

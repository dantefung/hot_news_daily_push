#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义后置处理器示例
展示如何实现自定义的后置处理逻辑
"""

import re
import logging
from typing import Dict, Any
from processor import PostProcessorInterface

logger = logging.getLogger(__name__)


class CustomSummaryProcessor(PostProcessorInterface):
    """
    自定义摘要处理器示例
    功能：添加时间戳、统计信息、格式化等
    """

    def __init__(self, add_timestamp=True, add_stats=True):
        """
        初始化自定义处理器

        Args:
            add_timestamp: 是否添加时间戳
            add_stats: 是否添加统计信息
        """
        self.add_timestamp = add_timestamp
        self.add_stats = add_stats

    def get_name(self) -> str:
        """获取处理器名称"""
        return "CustomSummaryProcessor"

    def get_priority(self) -> int:
        """获取处理器优先级"""
        return 20  # 在融合处理器之后执行

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """检查处理器是否启用"""
        return context.get('enable_custom_processor', True)

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 处理后的摘要内容
        """
        try:
            logger.info("开始执行自定义摘要处理")

            # 1. 添加时间戳
            if self.add_timestamp:
                summary = self._add_timestamp(summary, context)

            # 2. 添加统计信息
            if self.add_stats:
                summary = self._add_statistics(summary, context)

            # 3. 格式化处理
            summary = self._format_summary(summary)

            logger.info("自定义摘要处理完成")
            return summary

        except Exception as e:
            logger.error(f"自定义摘要处理失败: {e}")
            return summary

    def _add_timestamp(self, summary: str, context: Dict[str, Any]) -> str:
        """添加时间戳"""
        from datetime import datetime

        timestamp = context.get('timestamp', datetime.now().isoformat())
        timestamp_line = f"\n\n---\n*生成时间: {timestamp}*\n"

        return summary + timestamp_line

    def _add_statistics(self, summary: str, context: Dict[str, Any]) -> str:
        """添加统计信息"""
        deduplicated_content = context.get('deduplicated_content', [])

        if deduplicated_content:
            # 统计各来源的数量
            source_counts = {}
            for item in deduplicated_content:
                source_type = item.get('data_source_type', 'unknown')
                source_counts[source_type] = source_counts.get(
                    source_type, 0) + 1

            stats_lines = ["\n\n### 📊 数据统计"]
            for source_type, count in source_counts.items():
                stats_lines.append(f"- {source_type}: {count} 条")

            summary += "\n".join(stats_lines)

        return summary

    def _format_summary(self, summary: str) -> str:
        """格式化摘要"""
        # 确保标题格式一致
        summary = re.sub(r'^#\s*', '# ', summary, flags=re.MULTILINE)

        # 确保列表格式一致
        summary = re.sub(r'^\*\*\s*(\d+)\s*', r'** \1 ',
                         summary, flags=re.MULTILINE)

        return summary


class KeywordHighlighter(PostProcessorInterface):
    """
    关键词高亮处理器
    功能：为特定关键词添加高亮标记
    """

    def __init__(self, keywords=None):
        """
        初始化关键词高亮处理器

        Args:
            keywords: 要高亮的关键词列表
        """
        self.keywords = keywords or [
            'AI', '人工智能', '机器学习', '深度学习',
            'ChatGPT', 'OpenAI', 'Google', 'Microsoft',
            '区块链', '加密货币', 'Web3',
            '元宇宙', 'VR', 'AR', 'XR'
        ]

    def get_name(self) -> str:
        """获取处理器名称"""
        return "KeywordHighlighter"

    def get_priority(self) -> int:
        """获取处理器优先级"""
        return 30  # 在自定义处理器之后执行

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """检查处理器是否启用"""
        return context.get('enable_keyword_highlight', True)

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容，高亮关键词

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 处理后的摘要内容
        """
        try:
            logger.info("开始执行关键词高亮处理")

            highlighted_summary = summary

            for keyword in self.keywords:
                # 使用正则表达式进行不区分大小写的替换
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                highlighted_summary = pattern.sub(
                    f'**{keyword}**', highlighted_summary)

            logger.info("关键词高亮处理完成")
            return highlighted_summary

        except Exception as e:
            logger.error(f"关键词高亮处理失败: {e}")
            return summary


class ContentFilter(PostProcessorInterface):
    """
    内容过滤器
    功能：过滤或替换特定内容
    """

    def __init__(self, filters=None):
        """
        初始化内容过滤器

        Args:
            filters: 过滤规则列表，每个规则是一个元组 (pattern, replacement)
        """
        self.filters = filters or [
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[链接]'),
            (r'@[\w]+', '[用户]'),
            (r'#[\w]+', '[话题]'),
        ]

    def get_name(self) -> str:
        """获取处理器名称"""
        return "ContentFilter"

    def get_priority(self) -> int:
        """获取处理器优先级"""
        return 5  # 较高优先级，在其他处理器之前执行

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """检查处理器是否启用"""
        return context.get('enable_content_filter', False)  # 默认禁用

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容，应用过滤规则

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 处理后的摘要内容
        """
        try:
            logger.info("开始执行内容过滤处理")

            filtered_summary = summary

            for pattern, replacement in self.filters:
                filtered_summary = re.sub(
                    pattern, replacement, filtered_summary)

            logger.info("内容过滤处理完成")
            return filtered_summary

        except Exception as e:
            logger.error(f"内容过滤处理失败: {e}")
            return summary


# 使用示例
if __name__ == "__main__":
    from processor import register_post_processor

    # 注册自定义处理器
    custom_processor = CustomSummaryProcessor(
        add_timestamp=True, add_stats=True)
    keyword_highlighter = KeywordHighlighter()
    content_filter = ContentFilter()

    register_post_processor(custom_processor)
    register_post_processor(keyword_highlighter)
    register_post_processor(content_filter)

    print("✅ 自定义后置处理器注册完成")
    print("处理器列表:")
    print("- CustomSummaryProcessor: 添加时间戳和统计信息")
    print("- KeywordHighlighter: 关键词高亮")
    print("- ContentFilter: 内容过滤")

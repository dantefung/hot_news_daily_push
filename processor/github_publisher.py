#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub推送处理器
将处理后的摘要推送到GitHub仓库
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# 导入扩展点接口
from processor import PostProcessorInterface
# 导入GitHub工具类
from utils.github_utils import create_github_utils
# 导入配置
from config.config import (
    GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BRANCH, GITHUB_PATH
)

# 配置日志
logger = logging.getLogger(__name__)

# 定义代理配置
# proxies = {
#     "http": "http://127.0.0.1:1080",
#     "https": "http://127.0.0.1:1080"
# }
proxies = None

# 检查是否配置了代理
use_proxies = bool(proxies)


class GitHubPublisher(PostProcessorInterface):
    """
    GitHub推送处理器
    将摘要内容推送到GitHub仓库
    """

    def __init__(self, repo_owner=None, repo_name=None, branch="main", path="daily"):
        """
        初始化GitHub推送处理器

        Args:
            repo_owner: GitHub仓库所有者
            repo_name: GitHub仓库名称
            branch: 分支名称
            path: 文件保存路径
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.path = path
        self.github_utils = None
        self._load_config()

    def _load_config(self):
        """加载GitHub配置"""
        # 从config.py获取配置，优先使用传入参数，否则使用配置文件中的默认值
        self.repo_owner = self.repo_owner or GITHUB_REPO_OWNER
        self.repo_name = self.repo_name or GITHUB_REPO_NAME
        self.branch = self.branch or GITHUB_BRANCH
        self.path = self.path or GITHUB_PATH

        # 创建GitHub工具类实例
        self.github_utils = create_github_utils(
            token=GITHUB_TOKEN,
            repo_owner=self.repo_owner,
            repo_name=self.repo_name,
            branch=self.branch
        )

    def get_name(self) -> str:
        """获取处理器名称"""
        return "GitHubPublisher"

    def get_priority(self) -> int:
        """获取处理器优先级"""
        return 100  # 最后执行，确保内容已经处理完成

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """检查处理器是否启用"""
        return context.get('enable_github_publish', True) and self.github_utils.token is not None

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容并推送到GitHub

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 处理后的摘要内容（保持不变）
        """
        try:
            if not self._validate_config():
                logger.warning("GitHub配置不完整，跳过推送")
                return summary

            # 使用GitHub工具类发布每日总结
            success = self.github_utils.publish_daily_summary(summary, context)

            if success:
                logger.info(
                    f"✅ 成功推送到GitHub: {self.repo_owner}/{self.repo_name}")
            else:
                logger.error("❌ GitHub推送失败")

            return summary

        except Exception as e:
            logger.error(f"GitHub推送处理器执行失败: {str(e)}")
            return summary

    def _validate_config(self) -> bool:
        """验证GitHub配置"""
        if not self.github_utils.token:
            logger.warning("未配置GITHUB_TOKEN")
            return False

        if not self.repo_owner or not self.repo_name:
            logger.warning("未配置GITHUB_REPO_OWNER或GITHUB_REPO_NAME")
            return False

        return True

    def create_daily_summary(self, summary: str, context: Dict[str, Any]) -> bool:
        """
        创建每日总结文件

        Args:
            summary: 摘要内容
            context: 处理上下文

        Returns:
            bool: 是否成功
        """
        try:
            if not self._validate_config():
                return False

            # 使用GitHub工具类发布
            return self.github_utils.publish_daily_summary(summary, context)

        except Exception as e:
            logger.error(f"创建每日总结失败: {e}")
            return False


# 便捷函数
def create_github_publisher(repo_owner=None, repo_name=None, branch="main", path="daily"):
    """
    创建GitHub推送处理器

    Args:
        repo_owner: GitHub仓库所有者
        repo_name: GitHub仓库名称
        branch: 分支名称
        path: 文件保存路径

    Returns:
        GitHubPublisher: GitHub推送处理器实例
    """
    return GitHubPublisher(repo_owner, repo_name, branch, path)


if __name__ == "__main__":
    # 测试用例
    publisher = create_github_publisher()

    test_summary = """# 科技日报 - 2024-01-01

## ** 01 测试新闻 **
这是一个测试新闻的摘要内容。

## ** 02 另一个测试 **
这是另一个测试新闻的摘要内容。
"""

    test_context = {
        'summary_model': 'deepseek',
        'tech_only': True,
        'deduplicated_content': [{'title': '测试1'}, {'title': '测试2'}],
        'enable_github_publish': True
    }

    # 测试处理
    result = publisher.process(test_summary, test_context)
    print(f"处理结果长度: {len(result)}")

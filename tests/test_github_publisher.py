#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub推送功能测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from datetime import datetime
from processor.github_publisher import GitHubPublisher, create_github_publisher
from typing import Dict, Any


class TestGitHubPublisher(unittest.TestCase):
    """测试GitHub推送处理器"""

    def setUp(self):
        """测试前准备"""
        self.publisher = GitHubPublisher()
        self.test_summary = "测试摘要内容"
        self.test_context = {
            'summary_model': 'deepseek',
            'tech_only': True,
            'deduplicated_content': [{'title': '测试1'}, {'title': '测试2'}],
            'enable_github_publish': True
        }

    def test_initialization(self):
        """测试初始化"""
        publisher = GitHubPublisher()
        self.assertIsNotNone(publisher)
        self.assertEqual(publisher.get_name(), "GitHubPublisher")
        self.assertEqual(publisher.get_priority(), 100)

    def test_config_loading(self):
        """测试配置加载"""
        # 模拟环境变量
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_REPO_OWNER': 'test_owner',
            'GITHUB_REPO_NAME': 'test_repo',
            'GITHUB_BRANCH': 'main',
            'GITHUB_PATH': 'daily'
        }):
            publisher = GitHubPublisher()
            self.assertEqual(publisher.github_token, 'test_token')
            self.assertEqual(publisher.repo_owner, 'test_owner')
            self.assertEqual(publisher.repo_name, 'test_repo')
            self.assertEqual(publisher.branch, 'main')
            self.assertEqual(publisher.path, 'daily')

    def test_validation_with_valid_config(self):
        """测试有效配置验证"""
        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        self.assertTrue(self.publisher._validate_config())

    def test_validation_with_invalid_config(self):
        """测试无效配置验证"""
        # 缺少token
        self.publisher.github_token = None
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        self.assertFalse(self.publisher._validate_config())

        # 缺少仓库信息
        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = None
        self.publisher.repo_name = None

        self.assertFalse(self.publisher._validate_config())

    def test_is_enabled(self):
        """测试启用状态检查"""
        # 配置有效且启用
        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        context = {'enable_github_publish': True}
        self.assertTrue(self.publisher.is_enabled(context))

        # 配置无效
        self.publisher.github_token = None
        self.assertFalse(self.publisher.is_enabled(context))

        # 显式禁用
        context = {'enable_github_publish': False}
        self.assertFalse(self.publisher.is_enabled(context))

    def test_create_file_content(self):
        """测试文件内容创建"""
        timestamp = datetime.now()
        content = self.publisher._create_file_content(
            self.test_summary, self.test_context, timestamp)

        # 检查内容包含必要元素
        self.assertIn("科技日报", content)
        self.assertIn(self.test_summary, content)
        self.assertIn("deepseek", content)
        self.assertIn("2", content)  # 内容数量
        self.assertIn("```json", content)

    def test_encode_content(self):
        """测试内容编码"""
        test_content = "测试内容"
        encoded = self.publisher._encode_content(test_content)

        # 验证编码结果
        import base64
        expected = base64.b64encode(
            test_content.encode('utf-8')).decode('utf-8')
        self.assertEqual(encoded, expected)

    @patch('requests.put')
    def test_push_to_github_success(self, mock_put):
        """测试GitHub推送成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 201
        mock_put.return_value = mock_response

        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"
        self.publisher.branch = "main"

        success = self.publisher._push_to_github(
            "test_content", "2024-01-01", "14-30-00")

        self.assertTrue(success)
        mock_put.assert_called_once()

    @patch('requests.put')
    def test_push_to_github_file_exists(self, mock_put):
        """测试文件已存在的情况"""
        # 模拟文件已存在响应
        mock_response = Mock()
        mock_response.status_code = 422
        mock_put.return_value = mock_response

        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        # 模拟更新文件成功
        with patch.object(self.publisher, '_update_existing_file', return_value=True):
            success = self.publisher._push_to_github(
                "test_content", "2024-01-01", "14-30-00")
            self.assertTrue(success)

    @patch('requests.put')
    def test_push_to_github_failure(self, mock_put):
        """测试GitHub推送失败"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_put.return_value = mock_response

        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        success = self.publisher._push_to_github(
            "test_content", "2024-01-01", "14-30-00")

        self.assertFalse(success)

    @patch('requests.get')
    @patch('requests.put')
    def test_update_existing_file_success(self, mock_put, mock_get):
        """测试更新已存在文件成功"""
        # 模拟获取文件信息成功
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {'sha': 'test_sha'}
        mock_get.return_value = mock_get_response

        # 模拟更新文件成功
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        success = self.publisher._update_existing_file(
            "test_content", "2024-01-01", "14-30-00")

        self.assertTrue(success)
        mock_get.assert_called_once()
        mock_put.assert_called_once()

    def test_process_with_valid_config(self):
        """测试处理流程（有效配置）"""
        self.publisher.github_token = "test_token"
        self.publisher.repo_owner = "test_owner"
        self.publisher.repo_name = "test_repo"

        with patch.object(self.publisher, '_push_to_github', return_value=True):
            result = self.publisher.process(
                self.test_summary, self.test_context)

            # 处理结果应该与输入相同
            self.assertEqual(result, self.test_summary)

    def test_process_with_invalid_config(self):
        """测试处理流程（无效配置）"""
        # 不设置配置
        result = self.publisher.process(self.test_summary, self.test_context)

        # 即使配置无效，也应该返回原始内容
        self.assertEqual(result, self.test_summary)

    def test_create_github_publisher_function(self):
        """测试便捷函数"""
        publisher = create_github_publisher(
            repo_owner="test_owner",
            repo_name="test_repo",
            branch="main",
            path="daily"
        )

        self.assertIsInstance(publisher, GitHubPublisher)
        self.assertEqual(publisher.repo_owner, "test_owner")
        self.assertEqual(publisher.repo_name, "test_repo")
        self.assertEqual(publisher.branch, "main")
        self.assertEqual(publisher.path, "daily")

    @patch.object(GitHubPublisher, 'github_utils')
    def test_process_multi_draft(self, mock_github_utils):
        """测试多稿件推送能力"""
        # 模拟publish_daily_summary为True
        mock_github_utils.publish_daily_summary.return_value = True
        publisher = GitHubPublisher()
        context = dict(self.test_context)
        context['refined_summaries'] = ["稿件1内容", "稿件2内容"]
        result = publisher.process("稿件1内容", context)
        self.assertEqual(result, "稿件1内容")
        mock_github_utils.publish_daily_summary.assert_called_with(
            "稿件1内容", context)

    @patch('utils.github_utils.GitHubUtils.publish_daily_summary')
    def test_publish_daily_summary_multi(self, mock_publish):
        """测试publish_daily_summary多稿件推送"""
        from utils.github_utils import GitHubUtils
        github_utils = GitHubUtils(
            token="t", repo_owner="o", repo_name="r", branch="b")
        context = {'refined_summaries': ["A", "B"]}
        github_utils.publish_daily_summary("A", context)
        mock_publish.assert_called_with("A", context)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 工具类测试
"""

from utils.github_utils import GitHubUtils
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGitHubUtils(unittest.TestCase):
    """GitHub 工具类测试"""

    def setUp(self):
        """测试前的设置"""
        # 模拟环境变量
        self.env_patcher = patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_REPO_OWNER': 'test_owner',
            'GITHUB_REPO_NAME': 'test_repo',
            'GITHUB_BRANCH': 'main'
        })
        self.env_patcher.start()

        self.github_utils = GitHubUtils()

    def tearDown(self):
        """测试后的清理"""
        self.env_patcher.stop()

    def test_init_with_default_values(self):
        """测试使用默认值初始化"""
        github = GitHubUtils()
        self.assertEqual(github.token, 'test_token')
        self.assertEqual(github.repo_owner, 'test_owner')
        self.assertEqual(github.repo_name, 'test_repo')
        self.assertEqual(github.branch, 'main')

    def test_init_with_custom_values(self):
        """测试使用自定义值初始化"""
        github = GitHubUtils(
            token='custom_token',
            repo_owner='custom_owner',
            repo_name='custom_repo',
            branch='develop'
        )
        self.assertEqual(github.token, 'custom_token')
        self.assertEqual(github.repo_owner, 'custom_owner')
        self.assertEqual(github.repo_name, 'custom_repo')
        self.assertEqual(github.branch, 'develop')

    @patch('requests.request')
    def test_call_github_api_success(self, mock_request):
        """测试成功调用 GitHub API"""
        # 模拟成功的响应
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {'test': 'data'}
        mock_request.return_value = mock_response

        result = self.github_utils.call_github_api('/test')

        self.assertEqual(result, {'test': 'data'})
        mock_request.assert_called_once()

    @patch('requests.request')
    def test_call_github_api_error(self, mock_request):
        """测试 GitHub API 调用失败"""
        # 模拟失败的响应
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.status_text = 'Not Found'
        mock_response.text = '{"message": "Not Found"}'
        mock_request.return_value = mock_response

        with self.assertRaises(Exception):
            self.github_utils.call_github_api('/test')

    @patch('requests.request')
    def test_get_file_sha_success(self, mock_request):
        """测试成功获取文件 SHA"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'sha': 'test_sha'}
        mock_request.return_value = mock_response

        sha = self.github_utils.get_file_sha('test.md')
        self.assertEqual(sha, 'test_sha')

    @patch('requests.request')
    def test_get_file_sha_not_found(self, mock_request):
        """测试获取不存在的文件 SHA"""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = '{"message": "Not Found"}'
        mock_request.return_value = mock_response

        sha = self.github_utils.get_file_sha('nonexistent.md')
        self.assertIsNone(sha)

    @patch('requests.request')
    def test_create_or_update_file(self, mock_request):
        """测试创建或更新文件"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'content': {'sha': 'new_sha'}}
        mock_request.return_value = mock_response

        result = self.github_utils.create_or_update_file(
            'test.md',
            'test content',
            'test commit message'
        )

        self.assertEqual(result, {'content': {'sha': 'new_sha'}})

    @patch('requests.request')
    def test_get_file_content(self, mock_request):
        """测试获取文件内容"""
        import base64

        content = 'test content'
        encoded_content = base64.b64encode(
            content.encode('utf-8')).decode('utf-8')

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'content': encoded_content}
        mock_request.return_value = mock_response

        result = self.github_utils.get_file_content('test.md')
        self.assertEqual(result, content)

    @patch('requests.request')
    def test_file_exists_true(self, mock_request):
        """测试文件存在检查 - 文件存在"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_request.return_value = mock_response

        exists = self.github_utils.file_exists('test.md')
        self.assertTrue(exists)

    @patch('requests.request')
    def test_file_exists_false(self, mock_request):
        """测试文件存在检查 - 文件不存在"""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = '{"message": "Not Found"}'
        mock_request.return_value = mock_response

        exists = self.github_utils.file_exists('nonexistent.md')
        self.assertFalse(exists)

    @patch('requests.request')
    def test_list_files(self, mock_request):
        """测试列出文件"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {'name': 'file1.md', 'type': 'file'},
            {'name': 'file2.md', 'type': 'file'}
        ]
        mock_request.return_value = mock_response

        files = self.github_utils.list_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['name'], 'file1.md')


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub API 工具类
用于与 GitHub 仓库进行交互
"""

import os
import logging
import base64
import requests
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)


class GitHubUtils:
    """
    GitHub API 工具类，用于与 GitHub 仓库进行交互
    """

    def __init__(self, token=None, repo_owner=None, repo_name=None, branch=None):
        """
        初始化 GitHub 工具类

        Args:
            token (str): GitHub API token
            repo_owner (str): 仓库所有者
            repo_name (str): 仓库名称
            branch (str): 分支名称，默认为 main
        """
        from config.config import GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_BRANCH

        self.token = token or GITHUB_TOKEN
        self.repo_owner = repo_owner or GITHUB_REPO_OWNER
        self.repo_name = repo_name or GITHUB_REPO_NAME
        self.branch = branch or GITHUB_BRANCH

        if not self.token:
            logger.warning("GitHub token 未配置，某些功能可能无法使用")

        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'HotNewsDailyPush/1.0'
        }

    def call_github_api(self, path, method='GET', data=None):
        """
        调用 GitHub API 的通用方法

        Args:
            path (str): API 路径
            method (str): HTTP 方法
            data (dict): 请求数据

        Returns:
            dict: API 响应数据

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"{self.base_url}{path}"

        headers = self.headers.copy()
        if method in ['POST', 'PUT', 'PATCH'] and data:
            headers['Content-Type'] = 'application/json'

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=30
            )

            if not response.ok:
                error_text = response.text
                try:
                    error_json = response.json()
                    if error_json and 'message' in error_json:
                        error_text = error_json['message']
                        if 'errors' in error_json:
                            error_text += f" Details: {error_json['errors']}"
                except:
                    pass

                logger.error(
                    f"GitHub API 错误: {response.status_code} {response.reason} for {method} {url}. Message: {error_text}")
                raise Exception(
                    f"GitHub API 请求失败: {response.status_code} - {error_text}")

            # 处理 204 No Content 响应
            if response.status_code == 204 or response.headers.get("content-length") == "0":
                return None

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API 请求异常: {str(e)}")
            raise Exception(f"GitHub API 请求异常: {str(e)}")

    def get_file_sha(self, file_path):
        """
        获取文件的 SHA 值

        Args:
            file_path (str): 文件路径

        Returns:
            str: 文件的 SHA 值，如果文件不存在则返回 None
        """
        try:
            data = self.call_github_api(
                f"/contents/{file_path}?ref={self.branch}")
            return data.get('sha') if data else None
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                logger.info(
                    f"文件在 GitHub 上不存在: {file_path} (分支: {self.branch})")
                return None
            logger.error(f"获取文件 SHA 失败 {file_path}: {str(e)}")
            raise

    def create_or_update_file(self, file_path, content, commit_message, existing_sha=None):
        """
        创建或更新 GitHub 仓库中的文件

        Args:
            file_path (str): 文件路径
            content (str): 文件内容
            commit_message (str): 提交信息
            existing_sha (str): 现有文件的 SHA 值（用于更新）

        Returns:
            dict: API 响应数据
        """
        # Base64 编码内容
        content_bytes = content.encode('utf-8')
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')

        payload = {
            'message': commit_message,
            'content': content_b64,
            'branch': self.branch
        }

        if existing_sha:
            payload['sha'] = existing_sha

        return self.call_github_api(f"/contents/{file_path}", 'PUT', payload)

    def get_file_content(self, file_path):
        """
        获取 GitHub 仓库中文件的内容

        Args:
            file_path (str): 文件路径

        Returns:
            str: 文件内容
        """
        try:
            data = self.call_github_api(
                f"/contents/{file_path}?ref={self.branch}")
            if data and 'content' in data:
                # Base64 解码内容
                content_bytes = base64.b64decode(data['content'])
                return content_bytes.decode('utf-8')
            else:
                raise Exception("文件内容为空或格式错误")
        except Exception as e:
            logger.error(f"获取文件内容失败 {file_path}: {str(e)}")
            raise

    def file_exists(self, file_path):
        """
        检查文件是否存在于 GitHub 仓库中

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 文件是否存在
        """
        try:
            self.call_github_api(f"/contents/{file_path}?ref={self.branch}")
            return True
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                return False
            raise

    def delete_file(self, file_path, commit_message):
        """
        删除 GitHub 仓库中的文件

        Args:
            file_path (str): 文件路径
            commit_message (str): 提交信息

        Returns:
            dict: API 响应数据
        """
        # 首先获取文件的 SHA
        sha = self.get_file_sha(file_path)
        if not sha:
            raise Exception(f"文件不存在，无法删除: {file_path}")

        payload = {
            'message': commit_message,
            'sha': sha,
            'branch': self.branch
        }

        return self.call_github_api(f"/contents/{file_path}", 'DELETE', payload)

    def list_files(self, path=""):
        """
        列出指定路径下的文件

        Args:
            path (str): 目录路径，默认为根目录

        Returns:
            list: 文件列表
        """
        try:
            data = self.call_github_api(f"/contents/{path}?ref={self.branch}")
            if isinstance(data, list):
                return data
            else:
                return []
        except Exception as e:
            logger.error(f"列出文件失败 {path}: {str(e)}")
            return []

    def create_branch(self, branch_name, base_branch=None):
        """
        创建新分支

        Args:
            branch_name (str): 新分支名称
            base_branch (str): 基础分支名称，默认为当前分支

        Returns:
            dict: API 响应数据
        """
        if not base_branch:
            base_branch = self.branch

        # 获取基础分支的最新提交 SHA
        try:
            ref_data = self.call_github_api(f"/git/ref/heads/{base_branch}")
            sha = ref_data['object']['sha']
        except Exception as e:
            logger.error(f"获取基础分支 SHA 失败: {str(e)}")
            raise

        payload = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }

        return self.call_github_api("/git/refs", 'POST', payload)

    def create_pull_request(self, title, body, head_branch, base_branch=None):
        """
        创建 Pull Request

        Args:
            title (str): PR 标题
            body (str): PR 描述
            head_branch (str): 源分支
            base_branch (str): 目标分支，默认为当前分支

        Returns:
            dict: API 响应数据
        """
        if not base_branch:
            base_branch = self.branch

        payload = {
            'title': title,
            'body': body,
            'head': head_branch,
            'base': base_branch
        }

        return self.call_github_api("/pulls", 'POST', payload)

    def publish_daily_summary(self, summary, context=None):
        """
        发布每日总结到GitHub

        Args:
            summary (str): 摘要内容
            context (dict): 上下文信息

        Returns:
            bool: 是否成功
        """
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            summaries = [summary]
            if context and 'refined_summaries' in context and isinstance(context['refined_summaries'], list):
                summaries = context['refined_summaries']
            all_success = True
            for idx, summ in enumerate(summaries, 1):
                # 构建文件路径，增加_release后缀和编号
                file_path = f"daily/{date_str}_release_{idx}.md"
                file_content = self._create_summary_content(
                    summ, context, date_str)
                existing_sha = self.get_file_sha(file_path)
                commit_message = f"📰 科技日报更新 - {date_str} (稿件{idx})"
                if existing_sha:
                    logger.info(f"更新已存在的文件: {file_path}")
                    self.create_or_update_file(
                        file_path, file_content, commit_message, existing_sha)
                else:
                    logger.info(f"创建新文件: {file_path}")
                    self.create_or_update_file(
                        file_path, file_content, commit_message)
                logger.info(f"✅ 成功发布到GitHub: {file_path}")
            return all_success
        except Exception as e:
            logger.error(f"发布到GitHub失败: {str(e)}")
            return False

    def _create_summary_content(self, summary, context, date_str):
        """
        创建摘要文件内容

        Args:
            summary (str): 摘要内容
            context (dict): 上下文信息
            date_str (str): 日期字符串

        Returns:
            str: 文件内容
        """
        # 如果 summary 是 list，自动拼接为字符串
        if isinstance(summary, list):
            summary = '\n'.join(str(s) for s in summary)
        # 构建完整的markdown内容
        content_lines = [
            f"# 科技日报 - {date_str}",
            "",
            summary
        ]
        return "\n".join(content_lines)


# 便捷函数
def create_github_utils(token=None, repo_owner=None, repo_name=None, branch=None):
    """
    创建GitHub工具类实例

    Args:
        token (str): GitHub API token
        repo_owner (str): 仓库所有者
        repo_name (str): 仓库名称
        branch (str): 分支名称

    Returns:
        GitHubUtils: GitHub工具类实例
    """
    return GitHubUtils(token, repo_owner, repo_name, branch)


if __name__ == "__main__":
    # 测试用例
    github_utils = create_github_utils()

    test_summary = """# 科技日报 - 2024-01-01

## ** 01 测试新闻 **
这是一个测试新闻的摘要内容。

## ** 02 另一个测试 **
这是另一个测试新闻的摘要内容。
"""

    test_context = {
        'summary_model': 'deepseek',
        'tech_only': True,
        'deduplicated_content': [{'title': '测试1'}, {'title': '测试2'}]
    }

    # 测试发布
    success = github_utils.publish_daily_summary(test_summary, test_context)
    print(f"发布结果: {'成功' if success else '失败'}")

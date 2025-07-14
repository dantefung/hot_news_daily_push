#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的 GitHub 工具类测试
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_github_utils():
    """测试 GitHub 工具类"""
    try:
        from utils.github_utils import GitHubUtils

        # 设置测试环境变量
        os.environ['GITHUB_TOKEN'] = 'test_token'
        os.environ['GITHUB_REPO_OWNER'] = 'test_owner'
        os.environ['GITHUB_REPO_NAME'] = 'test_repo'
        os.environ['GITHUB_BRANCH'] = 'main'

        # 创建 GitHub 工具实例
        github = GitHubUtils()

        print("GitHub 工具类初始化成功")
        print(f"仓库所有者: {github.repo_owner}")
        print(f"仓库名称: {github.repo_name}")
        print(f"分支: {github.branch}")
        print(f"Token 已配置: {'是' if github.token else '否'}")

        return True

    except Exception as e:
        print(f"GitHub 工具类测试失败: {e}")
        return False


if __name__ == '__main__':
    success = test_github_utils()
    if success:
        print("✅ GitHub 工具类测试通过")
    else:
        print("❌ GitHub 工具类测试失败")

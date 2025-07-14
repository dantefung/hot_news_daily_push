#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub 工具类使用示例
"""

from utils.github_utils import GitHubUtils
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example_basic_usage():
    """基本使用示例"""
    print("=== GitHub 工具类基本使用示例 ===")

    # 创建 GitHub 工具实例
    github = GitHubUtils()

    # 检查配置
    print(f"仓库所有者: {github.repo_owner}")
    print(f"仓库名称: {github.repo_name}")
    print(f"分支: {github.branch}")
    print(f"Token 已配置: {'是' if github.token else '否'}")
    print()


def example_file_operations():
    """文件操作示例"""
    print("=== 文件操作示例 ===")

    github = GitHubUtils()

    # 示例文件路径
    test_file = "examples/test_file.md"

    # 检查文件是否存在
    if github.file_exists(test_file):
        print(f"文件 {test_file} 已存在")

        # 获取文件内容
        try:
            content = github.get_file_content(test_file)
            print(f"文件内容: {content[:100]}...")
        except Exception as e:
            print(f"获取文件内容失败: {e}")
    else:
        print(f"文件 {test_file} 不存在")

    print()


def example_create_update_file():
    """创建/更新文件示例"""
    print("=== 创建/更新文件示例 ===")

    github = GitHubUtils()

    # 示例文件路径
    test_file = "examples/example_file.md"

    # 准备文件内容
    content = f"""# 示例文件

这是一个通过 GitHub API 创建的示例文件。

创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 功能特性

- 自动创建文件
- 支持更新现有文件
- 完整的错误处理
- 中文支持

## 使用说明

```python
from utils.github_utils import GitHubUtils

github = GitHubUtils()
github.create_or_update_file(
    'path/to/file.md',
    '文件内容',
    '提交信息'
)
```
"""

    try:
        # 获取现有文件的 SHA（如果存在）
        existing_sha = github.get_file_sha(test_file)

        # 创建或更新文件
        commit_message = f"更新示例文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        result = github.create_or_update_file(
            test_file,
            content,
            commit_message,
            existing_sha
        )

        print(f"文件操作成功: {result.get('content', {}).get('sha', 'N/A')}")

    except Exception as e:
        print(f"文件操作失败: {e}")

    print()


def example_list_files():
    """列出文件示例"""
    print("=== 列出文件示例 ===")

    github = GitHubUtils()

    try:
        # 列出根目录文件
        files = github.list_files()
        print(f"根目录文件数量: {len(files)}")

        for file in files[:5]:  # 只显示前5个文件
            print(f"  - {file.get('name', 'N/A')} ({file.get('type', 'N/A')})")

        if len(files) > 5:
            print(f"  ... 还有 {len(files) - 5} 个文件")

    except Exception as e:
        print(f"列出文件失败: {e}")

    print()


def example_branch_operations():
    """分支操作示例"""
    print("=== 分支操作示例 ===")

    github = GitHubUtils()

    # 示例分支名称
    new_branch = f"example-branch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        # 创建新分支
        result = github.create_branch(new_branch)
        print(f"分支创建成功: {new_branch}")

        # 在新分支上创建文件
        test_file = f"examples/branch_test_{datetime.now().strftime('%Y%m%d')}.md"
        content = f"""# 分支测试文件

这个文件是在分支 {new_branch} 上创建的。

创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        github.create_or_update_file(
            test_file,
            content,
            f"在分支 {new_branch} 上创建测试文件",
            branch=new_branch
        )

        print(f"在分支 {new_branch} 上创建文件成功")

        # 创建 Pull Request
        pr_result = github.create_pull_request(
            title=f"示例 PR - {new_branch}",
            body=f"""
这是一个示例 Pull Request。

分支: {new_branch}
目标分支: {github.branch}
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 变更内容

- 创建了示例文件
- 演示了分支操作
- 展示了 PR 创建功能
            """,
            head_branch=new_branch
        )

        print(f"Pull Request 创建成功: {pr_result.get('html_url', 'N/A')}")

    except Exception as e:
        print(f"分支操作失败: {e}")

    print()


def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")

    # 使用无效的 token 创建实例
    github = GitHubUtils(token="invalid_token")

    try:
        # 尝试获取文件列表
        files = github.list_files()
        print("文件列表获取成功")
    except Exception as e:
        print(f"预期的错误: {e}")

    print()


def main():
    """主函数"""
    print("GitHub 工具类使用示例")
    print("=" * 50)
    print()

    # 运行各种示例
    example_basic_usage()
    example_file_operations()
    example_create_update_file()
    example_list_files()
    example_branch_operations()
    example_error_handling()

    print("示例运行完成！")


if __name__ == '__main__':
    main()

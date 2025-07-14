#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub推送功能使用示例
展示如何配置和使用GitHub推送处理器
"""

import os
import logging
from datetime import datetime
from processor import register_post_processor
from processor.github_publisher import create_github_publisher

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_github_publisher():
    """设置GitHub推送处理器"""

    # 方法1: 使用环境变量配置
    # 在 .env 文件中设置以下变量:
    # GITHUB_TOKEN=your_github_token
    # GITHUB_REPO_OWNER=your_username
    # GITHUB_REPO_NAME=your_repo_name
    # GITHUB_BRANCH=main
    # GITHUB_PATH=daily

    publisher = create_github_publisher()
    register_post_processor(publisher)

    logger.info("✅ GitHub推送处理器已注册（使用环境变量配置）")
    return publisher


def setup_github_publisher_with_params():
    """使用参数配置GitHub推送处理器"""

    # 方法2: 直接指定参数
    publisher = create_github_publisher(
        repo_owner="your_username",
        repo_name="your_repo_name",
        branch="main",
        path="daily"
    )
    register_post_processor(publisher)

    logger.info("✅ GitHub推送处理器已注册（使用参数配置）")
    return publisher


def test_github_publisher():
    """测试GitHub推送功能"""

    # 创建测试摘要
    test_summary = """# 科技日报 - 2024-01-01

## ** 01 OpenAI发布GPT-5 **
OpenAI今日宣布发布GPT-5，新模型在多个基准测试中表现优异，支持更长的上下文窗口和更强的推理能力。

## ** 02 Google推出Gemini 2.0 **
Google发布Gemini 2.0版本，在代码生成和数学推理方面有显著提升，同时降低了API调用成本。

## ** 03 微软发布Copilot更新 **
微软为GitHub Copilot推出重大更新，新增代码解释和重构建议功能，提升开发效率。
"""

    # 创建测试上下文
    test_context = {
        'summary_model': 'deepseek',
        'tech_only': True,
        'deduplicated_content': [
            {'title': 'OpenAI发布GPT-5', 'data_source_type': 'hotspot'},
            {'title': 'Google推出Gemini 2.0', 'data_source_type': 'rss'},
            {'title': '微软发布Copilot更新', 'data_source_type': 'twitter'}
        ],
        'enable_github_publish': True,
        'timestamp': datetime.now().isoformat()
    }

    # 创建处理器
    publisher = create_github_publisher()

    # 测试处理
    logger.info("开始测试GitHub推送功能...")
    result = publisher.process(test_summary, test_context)

    logger.info(f"处理完成，结果长度: {len(result)}")
    return result


def create_github_token_guide():
    """GitHub Token创建指南"""

    guide = """
# GitHub Token创建指南

## 1. 创建个人访问令牌

1. 登录GitHub，进入 Settings > Developer settings > Personal access tokens
2. 点击 "Generate new token" > "Generate new token (classic)"
3. 设置令牌名称，如 "Hot News Publisher"
4. 选择权限范围：
   - `repo` - 完整的仓库访问权限
   - 或者 `public_repo` - 仅公开仓库访问权限
5. 点击 "Generate token"
6. 复制生成的令牌（注意保存，页面关闭后无法再次查看）

## 2. 配置环境变量

在 .env 文件中添加：

```dotenv
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo_name
GITHUB_BRANCH=main
GITHUB_PATH=daily
```

## 3. 仓库准备

确保目标仓库存在，并且：
- 如果是私有仓库，确保Token有相应权限
- 如果是公开仓库，可以使用 `public_repo` 权限
- 目标分支存在（默认main分支）

## 4. 文件结构

推送后的文件将保存在：
```
your_repo/
└── daily/
    ├── 2024-01-01_14-30-00.md
    ├── 2024-01-01_18-45-30.md
    └── ...
```

## 5. 文件内容示例

推送的文件包含：
- 生成时间
- 使用的AI模型
- 内容统计信息
- 完整的摘要内容
- JSON格式的元数据
"""

    print(guide)


if __name__ == "__main__":
    print("GitHub推送功能示例")
    print("=" * 50)

    # 显示配置指南
    create_github_token_guide()

    print("\n" + "=" * 50)
    print("测试GitHub推送功能")

    # 检查环境变量
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️ 未配置GITHUB_TOKEN，跳过实际推送测试")
        print("请先配置GitHub Token后再运行测试")
    else:
        # 运行测试
        test_github_publisher()

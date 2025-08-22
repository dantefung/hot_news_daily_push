# GitHub 工具类使用指南

## 概述

`GitHubUtils` 是一个用于与 GitHub API 交互的 Python 工具类，提供了完整的文件操作、分支管理和 Pull Request 创建功能。

## 环境变量配置

在使用之前，需要在环境变量中配置以下参数：

```bash
# GitHub API Token（必需）
GITHUB_TOKEN=your_github_token_here

# GitHub 仓库信息（可选，有默认值）
GITHUB_REPO_OWNER=dantefung
GITHUB_REPO_NAME=daily-tech-articles
GITHUB_BRANCH=main
```

## 基本使用

### 1. 初始化

```python
from utils.github_utils import GitHubUtils

# 使用默认配置
github = GitHubUtils()

# 使用自定义配置
github = GitHubUtils(
    token="your_token",
    repo_owner="your_username",
    repo_name="your_repo",
    branch="develop"
)
```

### 2. 文件操作

#### 检查文件是否存在

```python
if github.file_exists("path/to/file.md"):
    print("文件存在")
else:
    print("文件不存在")
```

#### 获取文件内容

```python
try:
    content = github.get_file_content("path/to/file.md")
    print(content)
except Exception as e:
    print(f"获取文件失败: {e}")
```

#### 创建或更新文件

```python
content = "# 新文件内容\n\n这是一个测试文件。"
commit_message = "添加新文件"

try:
    # 获取现有文件的 SHA（如果存在）
    existing_sha = github.get_file_sha("path/to/file.md")
    
    result = github.create_or_update_file(
        "path/to/file.md",
        content,
        commit_message,
        existing_sha
    )
    print("文件操作成功")
except Exception as e:
    print(f"文件操作失败: {e}")
```

#### 删除文件

```python
try:
    github.delete_file("path/to/file.md", "删除文件")
    print("文件删除成功")
except Exception as e:
    print(f"删除文件失败: {e}")
```

### 3. 目录操作

#### 列出文件

```python
try:
    files = github.list_files("path/to/directory")
    for file in files:
        print(f"{file['name']} ({file['type']})")
except Exception as e:
    print(f"列出文件失败: {e}")
```

### 4. 分支操作

#### 创建新分支

```python
try:
    github.create_branch("new-feature-branch")
    print("分支创建成功")
except Exception as e:
    print(f"创建分支失败: {e}")
```

#### 创建 Pull Request

```python
try:
    pr_result = github.create_pull_request(
        title="新功能",
        body="这是一个新功能的 Pull Request",
        head_branch="new-feature-branch"
    )
    print(f"Pull Request 创建成功: {pr_result['html_url']}")
except Exception as e:
    print(f"创建 Pull Request 失败: {e}")
```

## 错误处理

工具类提供了完整的错误处理机制：

```python
try:
    result = github.call_github_api("/some/path")
except Exception as e:
    print(f"API 调用失败: {e}")
    # 处理错误...
```

## 完整示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.github_utils import GitHubUtils
from datetime import datetime

def main():
    # 初始化 GitHub 工具
    github = GitHubUtils()
    
    # 检查配置
    print(f"仓库: {github.repo_owner}/{github.repo_name}")
    print(f"分支: {github.branch}")
    
    # 创建示例文件
    content = f"""# 示例文件

创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是一个通过 GitHub API 创建的示例文件。
"""
    
    try:
        # 获取现有文件的 SHA
        existing_sha = github.get_file_sha("examples/sample.md")
        
        # 创建或更新文件
        result = github.create_or_update_file(
            "examples/sample.md",
            content,
            f"更新示例文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            existing_sha
        )
        
        print("文件操作成功")
        
        # 列出文件
        files = github.list_files("examples")
        print(f"examples 目录下有 {len(files)} 个文件")
        
    except Exception as e:
        print(f"操作失败: {e}")

if __name__ == "__main__":
    main()
```

## 注意事项

1. **Token 权限**: 确保你的 GitHub Token 有足够的权限来执行所需的操作
2. **API 限制**: GitHub API 有速率限制，避免频繁调用
3. **错误处理**: 始终使用 try-catch 来处理可能的异常
4. **文件路径**: 使用相对于仓库根目录的路径
5. **编码**: 文件内容会自动进行 UTF-8 编码处理

## 测试

运行测试来验证功能：

```bash
python tests/test_github_utils.py
```

## 运行示例

```bash
python examples/github_utils_example.py
```

## 功能特性

- ✅ 完整的文件操作（创建、读取、更新、删除）
- ✅ 分支管理（创建分支、创建 Pull Request）
- ✅ 目录浏览（列出文件）
- ✅ 完整的错误处理和日志记录
- ✅ 中文支持
- ✅ 自动 Base64 编码/解码
- ✅ 灵活的配置选项
- ✅ 详细的文档和示例

## 依赖项

- `requests`: HTTP 请求库
- `base64`: Base64 编码/解码
- `logging`: 日志记录

确保在 `requirements.txt` 中包含：

```
requests>=2.25.0
``` 

---

## post_merge_refine.py SEO标题自动生成说明

### 功能简介

`PostMergeRefineProcessor` 新增 `generate_seo_title(markdown_content, max_length=10)` 方法，可根据日报内容自动生成10字以内SEO友好标题。

### 用法示例

```python
from processor.post_merge_refine import PostMergeRefineProcessor

processor = PostMergeRefineProcessor()
with open('tests/test_data/2025-07-21_release_2.md', 'r', encoding='utf-8') as f:
    content = f.read()
seo_title = processor.generate_seo_title(content)
print(f"AI科技日报-2025-07-21 {seo_title}")
```

### 生成逻辑
- 优先提取“AI内容摘要”代码块内容
- 其次提取各小节标题（如“AI前沿研究”、“开源TOP项目”等）
- 再次提取高频关键词（如“安全”、“Agent”、“开源”等）
- 自动组合并截断，保证不超过10个中文字符
- 若无有效内容，兜底返回“AI创新日报”

### 场景建议
- 可用于日报网页、公众号、SEO优化等场景的标题自动生成
- 支持自定义最大长度

--- 
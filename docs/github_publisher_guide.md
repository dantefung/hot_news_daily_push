# GitHub推送功能使用指南

## 概述

GitHub推送功能是扩展点系统的一部分，可以将处理后的科技日报摘要自动推送到GitHub仓库。这个功能作为后置处理器，在AI总结完成后自动执行。

## 功能特点

- **自动推送**: 将摘要内容自动推送到指定的GitHub仓库
- **文件管理**: 按日期时间创建文件，自动处理文件冲突
- **元数据记录**: 包含生成时间、模型信息、内容统计等
- **配置灵活**: 支持自定义仓库、分支、路径等配置
- **智能更新**: 自动检测文件是否存在，支持更新已存在的文件

## 配置步骤

### 1. 创建GitHub个人访问令牌

1. 登录GitHub，进入 **Settings** > **Developer settings** > **Personal access tokens**
2. 点击 **"Generate new token"** > **"Generate new token (classic)"**
3. 设置令牌名称，如 "Hot News Publisher"
4. 选择权限范围：
   - `repo` - 完整的仓库访问权限（推荐）
   - 或者 `public_repo` - 仅公开仓库访问权限
5. 点击 **"Generate token"**
6. **重要**: 复制生成的令牌并妥善保存，页面关闭后无法再次查看

### 2. 配置环境变量

在 `.env` 文件中添加以下配置：

```dotenv
# --- GitHub推送配置 ---
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo_name
GITHUB_BRANCH=main
GITHUB_PATH=daily
```

### 3. 仓库准备

确保目标仓库存在，并且：
- 如果是私有仓库，确保Token有相应权限
- 如果是公开仓库，可以使用 `public_repo` 权限
- 目标分支存在（默认main分支）

## 文件结构

推送后的文件将保存在：

```
your_repo/
└── daily/
    ├── 2024-01-01_14-30-00.md
    ├── 2024-01-01_18-45-30.md
    ├── 2024-01-02_09-15-20.md
    └── ...
```

## 文件内容示例

推送的文件包含以下内容：

```markdown
# 科技日报 - 2024年01月01日

## ** 01 OpenAI发布GPT-5 **
OpenAI今日宣布发布GPT-5，新模型在多个基准测试中表现优异，支持更长的上下文窗口和更强的推理能力。

## ** 02 Google推出Gemini 2.0 **
Google发布Gemini 2.0版本，在代码生成和数学推理方面有显著提升，同时降低了API调用成本。

## ** 03 微软发布Copilot更新 **
微软为GitHub Copilot推出重大更新，新增代码解释和重构建议功能，提升开发效率。
```

## 使用方法

### 方法1: 使用环境变量配置（推荐）

```python
from processor import register_post_processor
from processor.github_publisher import create_github_publisher

# 注册GitHub推送处理器
publisher = create_github_publisher()
register_post_processor(publisher)
```

### 方法2: 直接指定参数

```python
from processor import register_post_processor
from processor.github_publisher import create_github_publisher

# 使用参数配置
publisher = create_github_publisher(
    repo_owner="your_username",
    repo_name="your_repo_name",
    branch="main",
    path="daily"
)
register_post_processor(publisher)
```

## 控制启用状态

### 通过环境变量

```dotenv
# 启用GitHub推送
ENABLE_GITHUB_PUBLISH=true
```

### 通过代码

```python
context = {
    'enable_github_publish': True,
    # 其他配置...
}
```

## 错误处理

GitHub推送处理器具有完善的错误处理机制：

1. **配置验证**: 自动检查Token和仓库配置是否完整
2. **网络错误**: 处理网络连接超时和API调用失败
3. **权限错误**: 处理Token权限不足或仓库访问被拒绝
4. **文件冲突**: 自动处理文件已存在的情况，支持更新
5. **容错机制**: 推送失败不影响主流程，继续使用原始摘要

## 常见问题

### Q: 推送失败，提示"Not Found"
A: 检查仓库名称和所有者是否正确，确保仓库存在且有访问权限

### Q: 推送失败，提示"Forbidden"
A: 检查Token权限是否足够，确保Token有仓库的写入权限

### Q: 推送失败，提示"Branch not found"
A: 检查分支名称是否正确，确保目标分支存在

### Q: 文件已存在但无法更新
A: 检查Token是否有仓库的写入权限，确保不是只读Token

### Q: 中文内容显示乱码
A: 确保文件使用UTF-8编码，系统会自动处理编码问题

## 测试

运行测试来验证配置：

```bash
python tests/test_github_publisher.py
```

或者运行示例：

```bash
python examples/github_publisher_example.py
```

## 安全注意事项

1. **Token安全**: 不要将Token提交到代码仓库，使用环境变量
2. **权限最小化**: 只授予必要的权限，避免过度授权
3. **定期更新**: 定期更新Token，提高安全性
4. **监控使用**: 定期检查Token的使用情况

## 高级配置

### 自定义文件路径

```python
publisher = create_github_publisher(
    path="tech-news/2024"  # 自定义路径
)
```

### 自定义分支

```python
publisher = create_github_publisher(
    branch="develop"  # 推送到develop分支
)
```

### 批量推送

```python
# 创建每日总结
success = publisher.create_daily_summary(summary, context)
```

## 集成到主流程

GitHub推送处理器已经集成到主流程中，会在以下时机自动执行：

1. AI总结完成后
2. 后置处理阶段
3. 按优先级顺序执行（优先级100，最后执行）

确保在运行主程序前配置好GitHub相关环境变量。 
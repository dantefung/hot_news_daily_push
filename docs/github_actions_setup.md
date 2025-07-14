# GitHub Actions 环境变量配置指南

本文档详细说明如何为 GitHub Actions 配置所需的环境变量。

## 📋 概述

本项目使用 GitHub Actions 进行自动化新闻收集、处理和推送。为了正常运行，需要在 GitHub Secrets 中配置相应的环境变量。

## 🔧 配置步骤

### 1. 进入 GitHub Secrets 配置页面

1. 打开你的 GitHub 仓库
2. 点击 `Settings` 标签页
3. 在左侧菜单中找到 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 按钮

### 2. 配置必需的环境变量

#### API 密钥配置

| 变量名            | 描述                   | 获取地址                                                     |
| ----------------- | ---------------------- | ------------------------------------------------------------ |
| `HUNYUAN_API_KEY` | 腾讯混元 API 密钥      | [腾讯云混元](https://cloud.tencent.com/product/hunyuan)      |
| `GEMINI_API_KEY`  | Google Gemini API 密钥 | [Google AI Studio](https://makersuite.google.com/app/apikey) |

#### Webhook 配置

| 变量名        | 描述             | 说明                            |
| ------------- | ---------------- | ------------------------------- |
| `WEBHOOK_URL` | 主要 Webhook URL | 用于推送成功通知的 Webhook 地址 |

#### 错误通知配置

| 变量名           | 描述               | 说明             |
| ---------------- | ------------------ | ---------------- |
| `ERROR_QYWX_KEY` | 企业微信机器人密钥 | 用于企业微信通知 |

#### GitHub 发布配置

| 变量名              | 描述                         | 说明                        |
| ------------------- | ---------------------------- | --------------------------- |
| `GITHUB_TOKEN`      | GitHub Personal Access Token | 用于访问 GitHub API 的令牌  |
| `GITHUB_REPO_OWNER` | GitHub 仓库所有者用户名      | 你的 GitHub 用户名          |
| `GITHUB_REPO_NAME`  | GitHub 仓库名称              | 当前仓库的名称              |
| `GITHUB_BRANCH`     | GitHub 分支名称              | 通常是 `main` 或 `master`   |
| `GITHUB_PATH`       | GitHub 发布路径              | 通常是 `daily` 或其他目录名 |

### 3. 配置可选的环境变量

#### API 密钥配置

| 变量名             | 描述              | 获取地址                                            |
| ------------------ | ----------------- | --------------------------------------------------- |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | [DeepSeek Platform](https://platform.deepseek.com/) |

#### Webhook 配置

| 变量名              | 描述             | 说明                            |
| ------------------- | ---------------- | ------------------------------- |
| `ERROR_WEBHOOK_URL` | 错误 Webhook URL | 用于推送失败通知的 Webhook 地址 |

#### 错误通知配置

| 变量名               | 描述               | 说明                   |
| -------------------- | ------------------ | ---------------------- |
| `ERROR_TG_BOT_TOKEN` | Telegram Bot Token | 用于 Telegram 通知     |
| `ERROR_TG_USER_ID`   | Telegram 用户 ID   | 接收通知的用户 ID      |
| `QYWX_ORIGIN`        | 企业微信来源标识   | 企业微信通知的来源标识 |

#### API 配置

| 变量名              | 描述              | 默认值                     |
| ------------------- | ----------------- | -------------------------- |
| `BASE_URL`          | 基础 URL 配置     | 自定义                     |
| `DEEPSEEK_API_URL`  | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL_ID` | DeepSeek 模型 ID  | `deepseek-chat`            |
| `GEMINI_MODEL_NAME` | Gemini 模型名称   | `gemini-2.0-flash-exp`     |
| `GEMINI_BASE_URL`   | Gemini 基础 URL   | `https://gemini.kbz.ink`   |

#### RSS 配置

| 变量名    | 描述       | 说明              |
| --------- | ---------- | ----------------- |
| `RSS_URL` | RSS 源 URL | 自定义 RSS 源地址 |

#### Crawl4AI 配置

| 变量名               | 描述              | 默认值                  |
| -------------------- | ----------------- | ----------------------- |
| `CRAWL4AI_ENABLED`   | 是否启用 Crawl4AI | `false`                 |
| `CRAWL4AI_API_URL`   | Crawl4AI API 地址 | `http://crawl.tuber.cc` |
| `CRAWL4AI_API_TOKEN` | Crawl4AI API 令牌 | `sk-tuber0613kobezhao`  |

## 🧪 配置验证

### 使用配置检查脚本

项目提供了一个配置检查脚本，可以验证所有环境变量是否正确配置：

```bash
python check_env_config.py
```

### 手动验证

1. 确保所有必需的环境变量都已配置
2. 手动触发 GitHub Actions workflow
3. 检查 Actions 日志确认配置正确
4. 查看生成的文件和通知是否正常

## 📝 配置示例

### 必需配置示例

```yaml
# 在 GitHub Secrets 中配置以下变量
HUNYUAN_API_KEY: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WEBHOOK_URL: https://hooks.slack.com/services/xxx/xxx/xxx
ERROR_QYWX_KEY: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_TOKEN: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO_OWNER: your-username
GITHUB_REPO_NAME: hot_news_daily_push
GITHUB_BRANCH: main
GITHUB_PATH: daily
```

### 可选配置示例

```yaml
# 可选配置（有默认值）
DEEPSEEK_API_KEY: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ERROR_WEBHOOK_URL: https://hooks.slack.com/services/xxx/xxx/xxx
ERROR_TG_BOT_TOKEN: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ERROR_TG_USER_ID: 123456789
QYWX_ORIGIN: hot_news_daily_push
BASE_URL: https://your-domain.com
RSS_URL: https://your-rss-feed.com
```

## ⚠️ 注意事项

1. **安全性**: 所有敏感信息（如 API 密钥）都应该通过 GitHub Secrets 配置，不要直接写在代码中
2. **权限**: 确保 GitHub Token 有足够的权限访问仓库和创建文件
3. **格式**: 环境变量名称必须完全匹配，区分大小写
4. **更新**: 如果修改了环境变量，需要重新触发 workflow 才能生效

## 🔍 故障排除

### 常见问题

1. **API 密钥无效**
   - 检查 API 密钥是否正确复制
   - 确认 API 密钥是否有效且未过期
   - 验证 API 服务是否可用

2. **Webhook 通知失败**
   - 检查 Webhook URL 是否正确
   - 确认 Webhook 服务是否正常运行
   - 验证网络连接是否正常

3. **GitHub 发布失败**
   - 检查 GitHub Token 权限是否足够
   - 确认仓库名称和分支名称是否正确
   - 验证目标路径是否存在

### 调试方法

1. 查看 GitHub Actions 日志
2. 使用配置检查脚本验证环境变量
3. 手动触发 workflow 进行测试
4. 检查生成的文件和通知

## 📚 相关文档

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitHub Secrets 配置指南](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [项目主文档](../README.md)
- [环境变量示例](../env_example.txt)

## 🤝 获取帮助

如果遇到配置问题，可以：

1. 查看项目的 Issues 页面
2. 提交新的 Issue 描述问题
3. 参考相关文档和示例
4. 联系项目维护者 
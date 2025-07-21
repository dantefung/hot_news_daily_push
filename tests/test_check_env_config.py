#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Actions 环境变量配置检查脚本
用于验证所有必需和可选的环境变量是否已正确配置
"""

import os
import sys
from typing import Dict, List, Tuple

# 必需的环境变量（程序运行必需的）
REQUIRED_ENV_VARS = {
    # API密钥配置
    "HUNYUAN_API_KEY": "腾讯混元 API密钥",
    "GEMINI_API_KEY": "Google Gemini API密钥",

    # Webhook配置
    "WEBHOOK_URL": "主要Webhook URL",

    # 错误通知配置
    "ERROR_QYWX_KEY": "企业微信机器人密钥",

    # GitHub发布配置
    "GITHUB_TOKEN": "GitHub Personal Access Token",
    "GITHUB_REPO_OWNER": "GitHub仓库所有者用户名",
    "GITHUB_REPO_NAME": "GitHub仓库名称",
    "GITHUB_BRANCH": "GitHub分支名称",
    "GITHUB_PATH": "GitHub发布路径"
}

# 可选的环境变量（有默认值或可以留空）
OPTIONAL_ENV_VARS = {
    # API密钥配置
    "DEEPSEEK_API_KEY": "DeepSeek API密钥",

    # Webhook配置
    "ERROR_WEBHOOK_URL": "错误Webhook URL",

    # 错误通知配置
    "ERROR_TG_BOT_TOKEN": "Telegram Bot Token",
    "ERROR_TG_USER_ID": "Telegram用户ID",
    "QYWX_ORIGIN": "企业微信来源标识",

    # API配置
    "BASE_URL": "基础URL配置",
    "DEEPSEEK_API_URL": "DeepSeek API地址",
    "DEEPSEEK_MODEL_ID": "DeepSeek模型ID",
    "GEMINI_MODEL_NAME": "Gemini模型名称",
    "GEMINI_BASE_URL": "Gemini基础URL",

    # RSS配置
    "RSS_URL": "RSS源URL",

    # Crawl4AI配置
    "CRAWL4AI_ENABLED": "是否启用Crawl4AI",
    "CRAWL4AI_API_URL": "Crawl4AI API地址",
    "CRAWL4AI_API_TOKEN": "Crawl4AI API令牌"
}

# 默认值配置
DEFAULT_VALUES = {
    "DEEPSEEK_API_URL": "https://api.deepseek.com",
    "DEEPSEEK_MODEL_ID": "deepseek-chat",
    "GEMINI_MODEL_NAME": "gemini-2.0-flash-exp",
    "GEMINI_BASE_URL": "https://gemini.kbz.ink",
    "CRAWL4AI_ENABLED": "false",
    "CRAWL4AI_API_URL": "http://crawl.tuber.cc",
    "CRAWL4AI_API_TOKEN": "sk-tuber0613kobezhao"
}


def check_environment_variables() -> Tuple[bool, Dict[str, List[str]]]:
    """
    检查环境变量配置

    Returns:
        Tuple[bool, Dict[str, List[str]]]: (是否通过检查, 检查结果详情)
    """
    results = {
        "missing_required": [],
        "missing_optional": [],
        "configured_required": [],
        "configured_optional": []
    }

    # 检查必需的环境变量
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.getenv(var_name)
        if value and value.strip():
            results["configured_required"].append(
                f"✅ {var_name}: {description}")
        else:
            results["missing_required"].append(f"❌ {var_name}: {description}")

    # 检查可选的环境变量
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.getenv(var_name)
        if value and value.strip():
            results["configured_optional"].append(
                f"✅ {var_name}: {description}")
        else:
            default_value = DEFAULT_VALUES.get(var_name, "未设置")
            results["missing_optional"].append(
                f"⚠️  {var_name}: {description} (默认值: {default_value})")

    # 判断是否通过检查
    passed = len(results["missing_required"]) == 0

    return passed, results


def print_check_results(passed: bool, results: Dict[str, List[str]]):
    """
    打印检查结果

    Args:
        passed: 是否通过检查
        results: 检查结果详情
    """
    print("=" * 60)
    print("🔍 GitHub Actions 环境变量配置检查")
    print("=" * 60)

    # 打印必需配置
    print("\n📋 必需配置 (Required):")
    print("-" * 40)
    if results["configured_required"]:
        for item in results["configured_required"]:
            print(item)

    if results["missing_required"]:
        print("\n❌ 缺失的必需配置:")
        for item in results["missing_required"]:
            print(item)

    # 打印可选配置
    print("\n📋 可选配置 (Optional):")
    print("-" * 40)
    if results["configured_optional"]:
        for item in results["configured_optional"]:
            print(item)

    if results["missing_optional"]:
        print("\n⚠️  未配置的可选配置 (将使用默认值):")
        for item in results["missing_optional"]:
            print(item)

    # 打印总结
    print("\n" + "=" * 60)
    if passed:
        print("🎉 配置检查通过！所有必需的环境变量都已配置。")
        print("✅ 可以安全地运行 GitHub Actions workflow。")
    else:
        print("❌ 配置检查失败！缺少必需的环境变量。")
        print("🔧 请在 GitHub Secrets 中配置缺失的必需变量。")
        print("\n📝 配置步骤:")
        print("1. 进入 GitHub 仓库的 Settings > Secrets and variables > Actions")
        print("2. 点击 'New repository secret'")
        print("3. 添加缺失的必需环境变量")
        print("4. 重新运行此检查脚本")

    print("=" * 60)


def generate_github_secrets_template():
    """
    生成 GitHub Secrets 配置模板
    """
    print("\n📋 GitHub Secrets 配置模板:")
    print("-" * 40)
    print("请在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加以下 Secrets:")
    print()

    print("🔑 必需 Secrets (Required):")
    for var_name, description in REQUIRED_ENV_VARS.items():
        print(f"  {var_name}: {description}")

    print("\n🔧 可选 Secrets (Optional):")
    for var_name, description in OPTIONAL_ENV_VARS.items():
        default_value = DEFAULT_VALUES.get(var_name, "未设置")
        print(f"  {var_name}: {description} (默认值: {default_value})")


def main():
    """主函数"""
    # 检查环境变量
    passed, results = check_environment_variables()

    # 打印检查结果
    print_check_results(passed, results)

    # 生成配置模板
    generate_github_secrets_template()

    # 返回退出码
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
后置处理组件使用示例
"""

from processor.post_merge_refine import post_process_summary
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def example_basic_usage():
    """基本使用示例"""
    print("=== 后置处理组件基本使用示例 ===")

    # 源文件路径
    summary_path = "data/outputs/formatted_summary_2025-07-11_01-21-02.md"

    # 输出文件路径
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H-%M-%S")
    output_path = f"data/outputs/final_refined_summary_{today}_{timestamp}.md"

    # 检查源文件是否存在
    if not os.path.exists(summary_path):
        print(f"⚠️  源文件不存在: {summary_path}")
        return False

    print(f"源文件: {summary_path}")
    print(f"输出文件: {output_path}")
    print(f"使用代理: https://api-proxy.me/gemini")

    # 执行后置处理
    success = post_process_summary(summary_path, output_path, "gemini")

    if success:
        print(f"✅ 后置处理完成: {output_path}")

        # 显示文件大小
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"输出文件大小: {file_size} 字节")
    else:
        print("❌ 后置处理失败")

    return success


def example_with_different_llm():
    """使用不同LLM的示例"""
    print("\n=== 使用不同LLM的示例 ===")

    summary_path = "data/outputs/formatted_summary_2025-07-11_01-21-02.md"

    if not os.path.exists(summary_path):
        print(f"⚠️  源文件不存在: {summary_path}")
        return

    # 测试不同的LLM
    llm_types = ["gemini", "deepseek", "hunyuan"]

    for llm_type in llm_types:
        print(f"\n--- 测试 {llm_type} ---")

        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H-%M-%S")
        output_path = f"data/outputs/final_refined_summary_{llm_type}_{today}_{timestamp}.md"

        try:
            success = post_process_summary(summary_path, output_path, llm_type)
            if success:
                print(f"✅ {llm_type} 处理完成: {output_path}")
            else:
                print(f"❌ {llm_type} 处理失败")
        except Exception as e:
            print(f"❌ {llm_type} 处理异常: {e}")


def example_custom_config():
    """自定义配置示例"""
    print("\n=== 自定义配置示例 ===")

    from processor.post_merge_refine import PostMergeRefineProcessor, create_llm_adapter

    # 创建自定义LLM适配器
    try:
        llm_adapter = create_llm_adapter("gemini")
        processor = PostMergeRefineProcessor(llm_integration=llm_adapter)

        # 自定义处理
        summary_path = "data/outputs/formatted_summary_2025-07-11_01-21-02.md"
        output_path = "data/outputs/custom_refined_summary.md"

        if os.path.exists(summary_path):
            success = processor.process(summary_path, output_path)
            if success:
                print(f"✅ 自定义处理完成: {output_path}")
            else:
                print("❌ 自定义处理失败")
        else:
            print(f"⚠️  源文件不存在: {summary_path}")

    except Exception as e:
        print(f"❌ 自定义配置失败: {e}")


def main():
    """主函数"""
    print("后置处理组件使用示例")
    print("=" * 50)

    # 运行基本示例
    example_basic_usage()

    # 运行不同LLM示例
    example_with_different_llm()

    # 运行自定义配置示例
    example_custom_config()

    print("\n" + "=" * 50)
    print("示例运行完成！")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 2025-07-21_release_2.md 测试 post_merge_refine.py 的主要功能（含AI润色和SEO标题）
"""
import os
import logging
from processor.post_merge_refine import PostMergeRefineProcessor, create_llm_adapter

def test_post_merge_refine_with_real_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 读取测试数据
    test_data_path = os.path.join(os.path.dirname(__file__), 'test_data', '2025-07-21_release_2.md')
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_summary = f.read()

    # 初始化LLM集成适配器（以Gemini为例）
    llm_adapter = create_llm_adapter("gemini")
    # 初始化处理器，注入llm_integration
    processor = PostMergeRefineProcessor(llm_integration=llm_adapter, enable_enhanced_processing=True)
    logger.info("处理器初始化成功")

    # 合并内容（此处只用本地内容，远程内容留空）
    merged_content = processor.merge_contents(test_summary, '', '')
    logger.info(f"合并内容完成，长度: {len(merged_content)} 字符")

    # AI润色（含SEO标题生成）
    refined_content = processor.ai_refine_content(merged_content)
    logger.info(f"AI润色完成，长度: {len(refined_content)} 字符")

    # 验证内容
    is_valid, validation_message = processor.validate_refined_content(refined_content)
    logger.info(f"内容验证: {is_valid}, 消息: {validation_message}")

    # 检查SEO标题是否已插入到一级标题
    first_line = refined_content.splitlines()[0]
    assert first_line.startswith("# AI科技日报-2025-07-21 "), "SEO标题未插入到一级标题！"

    # 保存结果
    output_path = os.path.join(os.path.dirname(__file__), 'test_data', '2025-07-21_refined_output.md')
    success = processor.save_refined_content(refined_content, output_path)
    logger.info(f"保存功能: {success}")
    
    assert is_valid, f"内容验证未通过: {validation_message}"
    assert success, "保存失败"
    print("✅ test_post_merge_refine_with_real_data 测试通过（含AI润色和SEO标题）")

    # 测试 process 方法（主流程）
    context = {'enable_post_process': True, 'refined_draft_count': 1}
    processed_content = processor.process(test_summary, context)
    logger.info(f"process方法处理完成，长度: {len(processed_content)} 字符")
    # 检查SEO标题是否已插入到一级标题
    first_line_proc = processed_content.splitlines()[0]
    assert first_line_proc.startswith("# AI科技日报-2025-07-21 "), "process方法未插入SEO标题！"
    print("✅ process方法测试通过（含SEO标题）")

if __name__ == "__main__":
    test_post_merge_refine_with_real_data() 
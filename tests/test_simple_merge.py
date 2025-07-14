#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试修复后的合并功能
"""

import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_simple_merge():
    """简单测试修复后的合并功能"""

    # 创建简单的测试内容
    local_summary = """
## AI洞察日报 2025/7/13

### **AI内容摘要**

```
OpenAI发布GPT-5，谷歌推出Gemini Pro。
```

### AI前沿研究

1. **OpenAI**发布了**GPT-5**！🚀这是最新的语言模型，性能大幅提升。

2. **谷歌**推出了**Gemini Pro**模型，支持多模态输入和输出。
"""

    remote1 = """
## AI前沿研究

3. **微软**发布了**Azure AI**服务更新，新增多项功能。

4. **亚马逊**推出了**AWS AI**服务，性能提升显著。
"""

    remote2 = """
## 开源TOP项目

1. **system-prompts-and-models-of-ai-tools**项目（已获62777颗星✨）汇集了Cursor、Devin等热门AI工具。

2. **storm**项目（已获24892颗星⭐）是一个由LLM驱动的知识管理系统。
"""

    try:
        # 导入后置处理器
        from processor.post_merge_refine import PostMergeRefineProcessor

        # 创建处理器实例
        processor = PostMergeRefineProcessor(enable_enhanced_processing=True)

        # 测试合并功能
        logger.info("测试合并功能...")
        merged_content = processor.merge_contents(
            local_summary, remote1, remote2)
        logger.info(f"✅ 合并内容完成，长度: {len(merged_content)} 字符")

        # 测试预处理功能
        logger.info("测试预处理功能...")
        preprocessed_content = processor.preprocess_content_for_ai(
            merged_content)
        logger.info(f"✅ 预处理完成，长度: {len(preprocessed_content)} 字符")

        # 保存结果
        os.makedirs("data/test", exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # 保存合并结果
        merged_path = f"data/test/simple_merged_{timestamp_str}.md"
        with open(merged_path, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        logger.info(f"✅ 合并结果已保存到: {merged_path}")

        # 保存预处理结果
        preprocessed_path = f"data/test/simple_preprocessed_{timestamp_str}.md"
        with open(preprocessed_path, 'w', encoding='utf-8') as f:
            f.write(preprocessed_content)
        logger.info(f"✅ 预处理结果已保存到: {preprocessed_path}")

        logger.info("🎉 简单测试完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = test_simple_merge()
    sys.exit(0 if success else 1)

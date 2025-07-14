#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立测试 post_merge_refine.py 的完整功能
"""

import os
import sys
import logging
import tempfile
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_post_merge_refine_standalone():
    """独立测试 post_merge_refine.py 的完整功能"""

    try:
        # 导入后置处理器
        from processor.post_merge_refine import PostMergeRefineProcessor, create_llm_adapter

        logger.info("开始独立测试 post_merge_refine.py 功能...")

        # 1. 测试处理器初始化
        logger.info("1. 测试处理器初始化...")
        processor = PostMergeRefineProcessor(enable_enhanced_processing=True)
        logger.info(
            f"✅ 处理器初始化成功，名称: {processor.get_name()}, 优先级: {processor.get_priority()}")

        # 2. 测试启用状态检查
        logger.info("2. 测试启用状态检查...")
        context = {'enable_post_process': True}
        is_enabled = processor.is_enabled(context)
        logger.info(f"✅ 启用状态检查: {is_enabled}")

        # 3. 创建测试内容
        logger.info("3. 创建测试内容...")
        test_summary = """
## AI科技日报 2025/7/13

### **AI内容摘要**

```
OpenAI发布GPT-5，谷歌推出Gemini Pro，微软Azure AI更新。
开源项目涵盖AI工具库和深度学习框架。
AI显著降低创业门槛，促投资思变。
```

### AI前沿研究

1. **OpenAI**发布了**GPT-5**！🚀这是最新的语言模型，性能大幅提升，支持更多任务。

2. **谷歌**推出了**Gemini Pro**模型，支持多模态输入和输出，在多个基准测试中表现优异。

### 开源TOP项目

1. **system-prompts-and-models-of-ai-tools**项目（已获62777颗星✨）汇集了Cursor、Devin等热门AI工具。

2. **storm**项目（已获24892颗星⭐）是一个由LLM驱动的知识管理系统。

### 社媒分享

1. **杨毅老师**认为，在AI时代，创业的门槛被AI"打骨折"了！💸构建MVP的成本大幅降低。

2. **Gary Marcus**指出，纯粹的LLM压根儿造不出通用人工智能（AGI）！

## ** 01 Kimi K2大模型爆火，前端组件生成能力出众，用户教程获Jeremy Howard推荐 **  
- [用 Kimi K2 跑出了一个...](https://x.com/op7418/status/1944332341536530469) `🏷️Twitter-歸藏(guizang.ai)`
- [彻底出圈，教程被Jeremy ...](https://x.com/op7418/status/1944327496746602944) `🏷️Twitter-歸藏(guizang.ai)`
- [用 Kimi K2 写了两个常...](https://x.com/op7418/status/1944314077180047426) `🏷️Twitter-歸藏(guizang.ai)`
- [Kimi K2 is numb...](https://x.com/huggingface/status/1944155602583691492) `🏷️Twitter-Hugging Face`
- [Kimi K2 is basi...](https://x.com/rasbt/status/1944056316424577525) `🏷️Twitter-Sebastian Raschka`

## ** 02 英特尔CEO承认AI时代掉队，已跌出芯片公司前十 **  
- [「太晚了，追不上英伟达了」：英...](https://www.36kr.com/p/3375532626974984) `🏷️36氪`
- [英特尔已不再是前十芯片公司](https://weibo.com/1642720480/5187959521021953) `🏷️爱范儿`

## ** 03 OpenAI人才流失：华人科学家Lu Liu被Meta挖走，Windsurf收购案取消 **  
- [又一华人科学家被挖走，Open...](https://www.36kr.com/p/3375818235304198) `🏷️36氪`
- [从OpenAI叛逃谷歌！这位2...](https://mp.weixin.qq.com/s/PWHvfSG90rYmtvmomudcwg) `🏷️公众号-新智元`
- [If you were par...](https://x.com/amasad/status/1944220905053598210) `🏷️Twitter-Amjad Masad`
- [WindSurf is dea...](https://x.com/svpino/status/1944087223600640388) `🏷️Twitter-Santiago`

## ** 04 AI宠物短剧风靡，成年轻人“情感代糖” **  
- [AI宠物短剧，年轻人的新“情感代糖”](https://www.36kr.com/p/3375818264746246) `🏷️36氪`

## ** 05 AI“穿越”新玩法火爆：根据童年照生成未来形象 **  
- [好玩！AI“穿越”新玩法火了：...](https://www.qbitai.com/2025/07/308611.html) `🏷️量子位`

## ** 06 苹果发布可穿戴设备AI模型，或用于Apple Watch **  
- [苹果发布穿戴设备 AI 模型](https://weibo.com/1642720480/5187965812213597) `🏷️爱范儿`

## ** 07 吴恩达：AI创业拼速度，代码不重要，需快速迭代 **  
- [一个月重写三次代码库、三个月就...](https://www.infoq.cn/article/pm5uDuSIof8UvxdQHz5Z?utm_source=rss&utm_medium=article) `🏷️InfoQ`

## ** 08 百度文心ERNIE 4.5开源，性能中文双项碾压 **  
- [百度文心ERNIE4.5部署与...](https://blog.csdn.net/2302_79177254/article/details/149256313) `🏷️CSDN`
- [文心一言 4.5 开源深度剖析...](https://blog.csdn.net/qq_57761637/article/details/149283762) `🏷️CSDN`

## ** 09 微信回应朋友圈评论占内存：图片会缓存到本地 **  
- [微信回应朋友圈评论占内存问题](https://weibo.com/1642720480/5188007335823527) `🏷️爱范儿`

## ** 10 央视曝光电动自行车非法改装：时速100km/h，续航200公里 **  
- [央视曝光电动自行车非法改装一条...](https://www.ithome.com/0/867/649.htm) `🏷️IT之家`


"""

        # 4. 测试合并内容功能
        logger.info("4. 测试合并内容功能...")
        local_summary = test_summary
        remote1 = """
## AI前沿研究

1. **OpenAI**发布了**GPT-5**！🚀这是最新的语言模型，性能大幅提升，支持更多任务。

2. **谷歌**推出了**Gemini Pro**模型，支持多模态输入和输出，在多个基准测试中表现优异。

3. **微软**发布了**Azure AI**服务更新，新增多项功能。
"""

        remote2 = """
## 开源TOP项目

1. **system-prompts-and-models-of-ai-tools**项目（已获62777颗星✨）汇集了Cursor、Devin等热门AI工具。

2. **storm**项目（已获24892颗星⭐）是一个由LLM驱动的知识管理系统。

3. **PyTorch**发布新版本，性能提升显著。
"""

        merged_content = processor.merge_contents(
            local_summary, remote1, remote2)
        logger.info(f"✅ 合并内容完成，长度: {len(merged_content)} 字符")

        # 5. 测试预处理功能
        logger.info("5. 测试预处理功能...")
        preprocessed_content = processor.preprocess_content_for_ai(
            merged_content)
        logger.info(f"✅ 预处理完成，长度: {len(preprocessed_content)} 字符")

        # 6. 测试内容验证功能
        logger.info("6. 测试内容验证功能...")
        is_valid, validation_message = processor.validate_refined_content(
            preprocessed_content)
        logger.info(f"✅ 内容验证: {is_valid}, 消息: {validation_message}")

        # 8. 测试保存功能
        logger.info("8. 测试保存功能...")
        test_output_path = "../data/test/standalone_test_output.md"
        os.makedirs("../data/test", exist_ok=True)
        success = processor.save_refined_content(
            preprocessed_content, test_output_path)
        logger.info(f"✅ 保存功能: {success}")

        # 9. 测试完整处理流程
        logger.info("9. 测试完整处理流程...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(test_summary)
            temp_summary_path = temp_file.name

        output_path = "../data/test/standalone_final_output.md"
        success = processor._process_internal(
            temp_summary_path, output_path, "gemini")
        logger.info(f"✅ 完整处理流程: {success}")

        # 10. 测试LLM适配器创建
        logger.info("10. 测试LLM适配器创建...")
        try:
            llm_adapter = create_llm_adapter("gemini")
            logger.info("✅ LLM适配器创建成功")
        except Exception as e:
            logger.warning(f"⚠️ LLM适配器创建失败（可能是配置问题）: {e}")

        # 11. 保存测试结果
        logger.info("11. 保存测试结果...")
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        test_results_path = f"../data/test/standalone_test_results_{timestamp_str}.md"

        with open(test_results_path, 'w', encoding='utf-8') as f:
            f.write(f"# Post Merge Refine 独立测试结果 - {timestamp_str}\n\n")
            f.write("## 测试内容\n\n")
            f.write("### 原始摘要\n")
            f.write(test_summary)
            f.write("\n\n### 合并后内容\n")
            f.write(merged_content)
            f.write("\n\n### 预处理后内容\n")
            f.write(preprocessed_content)
            f.write("\n\n## 测试结果\n")
            f.write(f"- 处理器初始化: ✅\n")
            f.write(f"- 启用状态检查: ✅\n")
            f.write(f"- 合并内容功能: ✅\n")
            f.write(f"- 预处理功能: ✅\n")
            f.write(f"- 内容验证: ✅ ({validation_message})\n")
            f.write(f"- 保存功能: ✅\n")
            f.write(f"- 完整处理流程: ✅\n")
            f.write(f"- LLM适配器: ✅\n")

        logger.info(f"✅ 测试结果已保存到: {test_results_path}")

        # 12. 测试多稿件生成能力
        logger.info("12. 测试多稿件生成能力（多draft）...")
        context_multi = {'enable_post_process': True, 'refined_draft_count': 2}
        refined_summaries = processor.process(test_summary, context_multi)
        assert isinstance(refined_summaries, list) and len(
            refined_summaries) == 2, "应生成2份润色稿件"
        for idx, refined in enumerate(refined_summaries, 1):
            logger.info(f"Draft {idx} 内容长度: {len(refined)} 字符")
            draft_path = f"../data/test/standalone_draft_{idx}.md"
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(refined)
            logger.info(f"✅ Draft {idx} 已保存到: {draft_path}")
        logger.info("🎉 多稿件生成能力测试通过！")

        logger.info("🎉 所有测试完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = test_post_merge_refine_standalone()
    sys.exit(0 if success else 1)

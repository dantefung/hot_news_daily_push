#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试混元AI润色功能
"""

import os
import sys
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.post_merge_refine import PostMergeRefineProcessor, create_llm_adapter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hunyuan_refine():
    """测试混元AI润色功能"""
    
    # 检查API密钥
    from config.config import HUNYUAN_API_KEY
    if not HUNYUAN_API_KEY:
        logger.warning("未设置HUNYUAN_API_KEY环境变量，跳过测试")
        return False
    
    try:
        # 创建混元AI适配器
        llm_adapter = create_llm_adapter("hunyuan")
        
        # 创建后置处理器
        processor = PostMergeRefineProcessor(llm_integration=llm_adapter)
        
        # 测试内容
        test_content = """
# AI科技日报-2025-01-27

## AI前沿研究

**OpenAI** 发布了最新的 **GPT-5** 模型，在多个基准测试中表现优异。

**Google DeepMind** 推出了 **Gemini Ultra 2.0**，在推理能力方面有显著提升。

## 开源TOP项目

**Llama 3.1** 开源项目获得了超过100万颗星，成为最受欢迎的开源AI模型。

**Stable Diffusion XL** 在图像生成质量方面取得了突破性进展。

## 社媒分享

**马斯克** 分享了关于AI安全性的重要观点，呼吁加强AI监管。

**Sam Altman** 讨论了AI在教育领域的应用前景。
"""
        
        # 构建润色prompt
        prompt = f"""
你是一位专业的科技新闻编辑，请对以下科技日报内容进行润色和优化。

{test_content}

请按照以下格式输出：

SEO标题: xxx

# AI科技日报-{datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d')}

> 🤖 AI科技日报 | ⏰ 每日精选 | 🌐 全球资讯 | 🔬 前沿探索 | 💡 深度分析 | 🛠️ 开源创新 | 🚀 未来展望 | [🌍 网页版↗️]

### **AI内容摘要**

```
[用2-3句话总结今日最重要的AI相关新闻要点]
```

### AI前沿研究

[按重要性排序，每条新闻用1-2段话描述]

### 开源TOP项目

[按重要性排序，每条项目用1-2段话描述]

### 社媒分享

[按重要性排序，每条分享用1-2段话描述]

---

**请确保：**
1. 内容生动有趣，使用emoji增强可读性
2. 按重要性合理排序
3. 格式完全符合上述模板
4. 直接输出markdown内容，不要添加任何确认语句或解释
"""
        
        # 调用混元AI进行润色
        logger.info("开始调用混元AI进行润色...")
        refined_content = llm_adapter.refine_markdown(prompt)
        
        # 保存结果
        timestamp_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "tests/test_data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"hunyuan_refine_test_{timestamp_str}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(refined_content)
        
        logger.info(f"混元AI润色测试完成，结果已保存到: {output_path}")
        logger.info(f"润色后内容长度: {len(refined_content)} 字符")
        
        # 验证结果
        if len(refined_content) > 100 and "AI科技日报" in refined_content:
            logger.info("✅ 混元AI润色测试成功")
            return True
        else:
            logger.error("❌ 混元AI润色测试失败：内容质量不符合预期")
            return False
            
    except Exception as e:
        logger.error(f"混元AI润色测试失败: {e}")
        return False

def test_hunyuan_integration():
    """测试混元AI集成功能"""
    
    try:
        # 创建混元AI适配器
        llm_adapter = create_llm_adapter("hunyuan")
        
        # 测试适配器初始化
        if llm_adapter.llm_type == "hunyuan":
            logger.info("✅ 混元AI适配器初始化成功")
        else:
            logger.error("❌ 混元AI适配器初始化失败")
            return False
        
        # 测试简单的prompt处理
        simple_prompt = "请简单介绍一下人工智能的发展历程。"
        result = llm_adapter.refine_markdown(simple_prompt)
        
        if result and len(result) > 10:
            logger.info("✅ 混元AI简单prompt测试成功")
            return True
        else:
            logger.error("❌ 混元AI简单prompt测试失败")
            return False
            
    except Exception as e:
        logger.error(f"混元AI集成测试失败: {e}")
        return False

def test_hunyuan_summarize():
    """测试混元AI摘要功能"""
    
    # 检查API密钥
    from config.config import HUNYUAN_API_KEY
    if not HUNYUAN_API_KEY:
        logger.warning("未设置HUNYUAN_API_KEY环境变量，跳过测试")
        return False
    
    try:
        from llm_integration.hunyuan_integration import summarize_with_hunyuan
        
        # 测试数据
        test_hotspots = [
            {
                'title': 'OpenAI发布GPT-5模型，性能大幅提升',
                'source': 'TechCrunch',
                'summary': 'OpenAI今日发布了最新的GPT-5模型，相比GPT-4在推理能力和多模态处理方面有显著提升。'
            },
            {
                'title': '谷歌推出Gemini 2.0，支持更复杂的多模态任务',
                'source': 'Google Blog',
                'summary': '谷歌发布了Gemini 2.0版本，新模型在图像理解、视频分析等任务上表现优异。'
            },
            {
                'title': 'Meta发布Llama 3.5，开源大模型再升级',
                'source': 'Meta AI',
                'summary': 'Meta发布了Llama 3.5模型，在多个基准测试中超越了GPT-4的性能。'
            }
        ]
        
        logger.info("开始测试混元AI摘要功能...")
        result = summarize_with_hunyuan(test_hotspots, HUNYUAN_API_KEY, max_retries=3, tech_only=True)
        
        # 保存结果
        timestamp_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "tests/test_data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"hunyuan_summarize_test_{timestamp_str}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"混元AI摘要测试完成，结果已保存到: {output_path}")
        logger.info(f"摘要内容长度: {len(result)} 字符")
        
        # 验证结果
        if len(result) > 50:
            logger.info("✅ 混元AI摘要测试成功")
            return True
        else:
            logger.error("❌ 混元AI摘要测试失败：内容质量不符合预期")
            return False
            
    except Exception as e:
        logger.error(f"混元AI摘要测试失败: {e}")
        return False

def test_hunyuan_content_summary():
    """测试混元AI内容摘要功能"""
    
    # 检查API密钥
    from config.config import HUNYUAN_API_KEY
    if not HUNYUAN_API_KEY:
        logger.warning("未设置HUNYUAN_API_KEY环境变量，跳过测试")
        return False
    
    try:
        from llm_integration.hunyuan_integration import summarize_with_tencent_hunyuan
        
        # 测试内容
        test_content = """
OpenAI今日发布了最新的GPT-5模型，相比GPT-4在推理能力和多模态处理方面有显著提升。
新模型在多个基准测试中表现优异，特别是在数学推理、代码生成和创意写作方面。
GPT-5还增强了对图像、音频和视频的理解能力，支持更复杂的多模态任务。
该模型已经在OpenAI的API平台上开放使用，开发者可以立即开始集成。
"""
        
        logger.info("开始测试混元AI内容摘要功能...")
        result = summarize_with_tencent_hunyuan(test_content, HUNYUAN_API_KEY, title="OpenAI发布GPT-5模型")
        
        logger.info(f"混元AI内容摘要测试完成")
        logger.info(f"摘要: {result.get('summary', '')}")
        logger.info(f"科技相关: {result.get('is_tech', False)}")
        
        # 验证结果
        if result.get('summary') and len(result.get('summary', '')) > 10:
            logger.info("✅ 混元AI内容摘要测试成功")
            return True
        else:
            logger.error("❌ 混元AI内容摘要测试失败：内容质量不符合预期")
            return False
            
    except Exception as e:
        logger.error(f"混元AI内容摘要测试失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始测试混元AI功能...")
    
    # 测试集成功能
    integration_success = test_hunyuan_integration()
    
    # 测试润色功能
    refine_success = test_hunyuan_refine()
    
    # 测试摘要功能
    summarize_success = test_hunyuan_summarize()
    
    # 测试内容摘要功能
    content_summary_success = test_hunyuan_content_summary()
    
    if integration_success and refine_success and summarize_success and content_summary_success:
        logger.info("🎉 所有混元AI测试通过")
    else:
        logger.error("❌ 部分混元AI测试失败")
        sys.exit(1)

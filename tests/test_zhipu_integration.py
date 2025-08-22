#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试智谱清言API集成
"""

import os
import sys
import json
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_integration.zhipu_integration import summarize_with_zhipu

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_zhipu_integration():
    """
    测试智谱清言API集成
    """
    # 模拟热点数据
    test_hotspots = [
        {
            "title": "OpenAI发布GPT-5模型，性能大幅提升",
            "url": "https://example.com/news1",
            "source": "techcrunch",
            "summary": "OpenAI发布了最新的GPT-5模型，在多个基准测试中表现优异"
        },
        {
            "title": "谷歌推出新的AI助手Gemini Advanced",
            "url": "https://example.com/news2", 
            "source": "theverge",
            "summary": "谷歌发布了Gemini Advanced，这是一个更强大的AI助手"
        },
        {
            "title": "微软投资OpenAI 100亿美元",
            "url": "https://example.com/news3",
            "source": "reuters",
            "summary": "微软宣布向OpenAI投资100亿美元，深化AI合作"
        }
    ]
    
    # 从环境变量获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        logger.warning("未设置ZHIPU_API_KEY环境变量，跳过API测试")
        return
    
    try:
        logger.info("开始测试智谱清言API集成...")
        
        # 测试科技新闻模式
        result = summarize_with_zhipu(
            hotspots=test_hotspots,
            api_key=api_key,
            model_id="glm-4.5-flash",
            max_retries=2,
            tech_only=True
        )

        logger.info("智谱清言API测试成功!")
        logger.info(f"返回结果长度: {len(result)} 字符")
        logger.info(f"result: {result}")
        logger.info("结果预览:")
        logger.info(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        logger.error(f"智谱清言API测试失败: {str(e)}")

if __name__ == "__main__":
    test_zhipu_integration()

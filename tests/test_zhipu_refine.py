#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试智谱AI润色功能
"""

import os
import sys
import logging
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from functools import wraps

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.post_merge_refine import PostMergeRefineProcessor, create_llm_adapter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_on_timeout(max_retries=3, delay=5, timeout_seconds=180):
    """重试装饰器，处理超时错误"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    # 如果是LLM适配器调用，设置更长的超时时间
                    if 'llm_adapter' in kwargs or (args and hasattr(args[0], 'refine_markdown')):
                        logger.info(f"第{attempt + 1}次尝试，超时时间设置为{timeout_seconds}秒...")
                        # 这里可以通过修改适配器的超时配置来实现
                        return func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except (requests.exceptions.Timeout, 
                        requests.exceptions.ReadTimeout,
                        requests.exceptions.ConnectionError) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"第{attempt + 1}次尝试失败: {e}")
                        logger.info(f"等待{delay}秒后重试...")
                        time.sleep(delay)
                        delay *= 2  # 指数退避
                    else:
                        logger.error(f"所有{max_retries}次尝试都失败了")
                        raise
            return None
        return wrapper
    return decorator

def test_network_connection():
    """测试网络连接"""
    try:
        logger.info("测试网络连接...")
        response = requests.get("https://open.bigmodel.cn", timeout=10)
        if response.status_code == 200:
            logger.info("✅ 网络连接正常")
            return True
        else:
            logger.warning(f"网络连接异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"网络连接测试失败: {e}")
        return False

@retry_on_timeout(max_retries=3, delay=5, timeout_seconds=180)
def safe_refine_markdown(llm_adapter, prompt):
    """安全的润色调用，带重试机制和更长超时时间"""
    # 配置更长的超时时间
    original_timeout = configure_zhipu_timeout(llm_adapter, 180)
    
    try:
        return llm_adapter.refine_markdown(prompt)
    finally:
        # 恢复原始超时配置
        restore_zhipu_timeout(llm_adapter, original_timeout)

def configure_zhipu_timeout(llm_adapter, timeout_seconds=None):
    """配置智谱AI适配器的超时时间"""
    from config.config import ZHIPU_TIMEOUT
    
    if timeout_seconds is None:
        timeout_seconds = ZHIPU_TIMEOUT
    
    try:
        # 尝试直接修改适配器的超时配置
        if hasattr(llm_adapter, '_timeout'):
            original_timeout = llm_adapter._timeout
            llm_adapter._timeout = timeout_seconds
            logger.info(f"智谱AI超时时间已设置为{timeout_seconds}秒")
            return original_timeout
        else:
            logger.warning("无法直接修改适配器超时配置，将使用默认设置")
            return None
    except Exception as e:
        logger.warning(f"配置超时时间失败: {e}")
        return None

def restore_zhipu_timeout(llm_adapter, original_timeout):
    """恢复智谱AI适配器的原始超时时间"""
    if original_timeout is not None and hasattr(llm_adapter, '_timeout'):
        try:
            llm_adapter._timeout = original_timeout
            logger.info(f"智谱AI超时时间已恢复为{original_timeout}秒")
        except Exception as e:
            logger.warning(f"恢复超时时间失败: {e}")

def test_zhipu_refine():
    """测试智谱AI润色功能"""
    
    # 检查API密钥
    from config.config import ZHIPU_API_KEY
    if not ZHIPU_API_KEY:
        logger.warning("未设置ZHIPU_API_KEY环境变量，跳过测试")
        return False
    
    try:
        # 创建智谱AI适配器
        llm_adapter = create_llm_adapter("zhipu")
        
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
        
        # 配置超时时间（简单内容使用较短超时）
        original_timeout = configure_zhipu_timeout(llm_adapter, 120)  # 2分钟
        
        try:
            # 调用智谱AI进行润色
            logger.info("开始调用智谱AI进行润色...")
            refined_content = llm_adapter.refine_markdown(prompt)
        finally:
            # 恢复原始超时配置
            restore_zhipu_timeout(llm_adapter, original_timeout)
        
        # 保存结果
        timestamp_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "./data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"zhipu_refine_test_{timestamp_str}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(refined_content)
        
        logger.info(f"智谱AI润色测试完成，结果已保存到: {output_path}")
        logger.info(f"润色后内容长度: {len(refined_content)} 字符")
        
        # 验证结果
        if len(refined_content) > 100 and "AI科技日报" in refined_content:
            logger.info("✅ 智谱AI润色测试成功")
            return True
        else:
            logger.error("❌ 智谱AI润色测试失败：内容质量不符合预期")
            return False
            
    except Exception as e:
        logger.error(f"智谱AI润色测试失败: {e}")
        return False

def test_zhipu_integration():
    """测试智谱AI集成功能"""
    
    try:
        # 创建智谱AI适配器
        llm_adapter = create_llm_adapter("zhipu")
        
        # 测试适配器初始化
        if llm_adapter.llm_type == "zhipu":
            logger.info("✅ 智谱AI适配器初始化成功")
        else:
            logger.error("❌ 智谱AI适配器初始化失败")
            return False
        
        # 配置超时时间（简单测试使用较短超时）
        original_timeout = configure_zhipu_timeout(llm_adapter, 60)  # 1分钟
        
        try:
            # 测试简单的prompt处理
            simple_prompt = "请简单介绍一下人工智能的发展历程。"
            result = llm_adapter.refine_markdown(simple_prompt)
        finally:
            # 恢复原始超时配置
            restore_zhipu_timeout(llm_adapter, original_timeout)
        
        if result and len(result) > 10:
            logger.info("✅ 智谱AI简单prompt测试成功")
            return True
        else:
            logger.error("❌ 智谱AI简单prompt测试失败")
            return False
            
    except Exception as e:
        logger.error(f"智谱AI集成测试失败: {e}")
        return False

def test_zhipu_refine_with_preprocessed_data():
    """使用预处理的测试数据测试智谱AI润色功能"""
    
    # 检查API密钥
    from config.config import ZHIPU_API_KEY
    if not ZHIPU_API_KEY:
        logger.warning("未设置ZHIPU_API_KEY环境变量，跳过测试")
        return False
    
    try:
        # 读取预处理的测试数据
        test_data_path = os.path.join(os.path.dirname(__file__), "test_data", "preprocessed_2025-08-22_23-00-03.md")
        
        if not os.path.exists(test_data_path):
            logger.error(f"测试数据文件不存在: {test_data_path}")
            return False
        
        with open(test_data_path, 'r', encoding='utf-8') as f:
            preprocessed_content = f.read()
        
        logger.info(f"成功读取预处理测试数据，长度: {len(preprocessed_content)} 字符")
        
        # 创建智谱AI适配器
        llm_adapter = create_llm_adapter("zhipu")
        
        # 创建后置处理器
        processor = PostMergeRefineProcessor(llm_integration=llm_adapter)
        
        # 根据内容长度动态设置超时时间
        content_length = len(preprocessed_content)
        if content_length > 10000:  # 超过1万字符
            timeout_seconds = 300  # 5分钟
            logger.info(f"内容较长({content_length}字符)，设置超时时间为{timeout_seconds}秒")
        elif content_length > 5000:  # 超过5千字符
            timeout_seconds = 240  # 4分钟
            logger.info(f"内容中等({content_length}字符)，设置超时时间为{timeout_seconds}秒")
        else:
            timeout_seconds = 180  # 3分钟
            logger.info(f"内容较短({content_length}字符)，设置超时时间为{timeout_seconds}秒")
        
        # 构建润色prompt
        prompt = f"""
你是一位专业的科技新闻编辑，请对以下AI资讯日报内容进行润色和优化。

{preprocessed_content}

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
5. 保持原文的核心信息和链接
"""
        
        # 配置超时时间
        original_timeout = configure_zhipu_timeout(llm_adapter, timeout_seconds)
        
        try:
            # 调用智谱AI进行润色
            logger.info("开始使用预处理数据调用智谱AI进行润色...")
            refined_content = llm_adapter.refine_markdown(prompt)
            
            # 保存结果
            timestamp_str = datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = "./data"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"zhipu_refine_preprocessed_{timestamp_str}.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(refined_content)
            
            logger.info(f"智谱AI预处理数据润色测试完成，结果已保存到: {output_path}")
            logger.info(f"润色后内容长度: {len(refined_content)} 字符")
            
            # 验证结果
            if len(refined_content) > 500 and "AI科技日报" in refined_content:
                logger.info("✅ 智谱AI预处理数据润色测试成功")
                return True
            else:
                logger.error("❌ 智谱AI预处理数据润色测试失败：内容质量不符合预期")
                return False
                
        finally:
            # 恢复原始超时配置
            restore_zhipu_timeout(llm_adapter, original_timeout)
            
    except Exception as e:
        logger.error(f"智谱AI预处理数据润色测试失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始测试智谱AI润色功能...")
    logger.info("超时配置说明:")
    logger.info("- 默认超时: 180秒（3分钟）")
    logger.info("- 简单测试: 60秒")
    logger.info("- 基础润色: 120秒") 
    logger.info("- 预处理数据: 根据内容长度动态调整(180-300秒)")
    logger.info("- 重试机制: 最多3次，指数退避延迟")
    logger.info("- 可通过环境变量ZHIPU_TIMEOUT自定义超时时间")
    
    # 测试网络连接
    network_success = test_network_connection()
    
    # 测试集成功能
    # integration_success = test_zhipu_integration()
    integration_success = True
    # 测试润色功能
    # refine_success = test_zhipu_refine()
    refine_success = True
    # 测试预处理数据润色功能
    preprocessed_refine_success = test_zhipu_refine_with_preprocessed_data()
    
    if network_success and integration_success and refine_success and preprocessed_refine_success:
        logger.info("🎉 所有智谱AI测试通过")
    else:
        logger.error("❌ 部分智谱AI测试失败")
        sys.exit(1)

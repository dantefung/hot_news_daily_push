#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
混元新闻内容总结：使用混元对爬取的内容进行摘要总结和mark
"""

import json
import logging
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from utils.utils import get_content_hash, load_summary_cache, save_summary_cache

# 配置日志
logger = logging.getLogger(__name__)

def summarize_with_tencent_hunyuan(content, api_key, title="", max_retries=3, use_cache=True):
    """
    使用腾讯混元turbo-S模型对内容进行概述总结
    返回JSON格式，包含摘要和科技相关性判断
    支持缓存机制，避免重复处理相同内容
    """
    if not content or len(content.strip()) < 50:
        logger.warning(f"内容过短或为空，跳过摘要生成: {content[:50]}...")
        return {"summary": "", "is_tech": False}
    
    # 计算内容哈希值用于缓存
    content_hash = get_content_hash(content[:2000])  # 只对前2000字符计算哈希
    
    # 如果启用缓存，尝试从缓存中获取结果
    if use_cache and content_hash:
        # 加载缓存
        summary_cache = load_summary_cache()
        
        # 检查缓存中是否有对应的结果
        if content_hash in summary_cache:
            cached_result = summary_cache[content_hash]
            logger.info(f"从缓存中获取摘要: {cached_result['summary'][:30]}...")
            return cached_result
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 记录要发送的内容长度
            logger.info(f"发送至混元模型的内容长度: {len(content[:2000])} 字符")
            
            # 创建LLM实例，添加正确的base_url
            llm = ChatOpenAI(
                model="hunyuan-lite",  # 使用hunyuan-turboS模型
                # model="hunyuan-turbos-latest",  # 使用hunyuan-turboS模型
                temperature=0.3,
                api_key=api_key,
                max_tokens=150,
                base_url="https://api.hunyuan.cloud.tencent.com/v1"  # 添加混元API的base_url
            )
            
            # 创建提示模板，要求返回JSON格式
            prompt = PromptTemplate(
                input_variables=["content", "title"],
                template="""请对以下新闻内容进行简洁概述，并判断是否与科技相关（包括AI、人工智能、互联网、软件、硬件、电子产品等）。请优先通过新闻标题来判断是否与科技相关，如果标题中没有科技相关的关键词，请通过新闻内容来判断。
                    
                    新闻标题：{title}
                    新闻内容：
                    {content}
                    
                    请以JSON格式返回，包含以下字段：
                    1. summary: 新闻摘要，不超过150个字
                    2. is_tech: 布尔值，表示是否与科技相关

                    只返回JSON格式，不要有任何额外说明。
                    """
            )
            
            # 创建LLMChain
            chain = LLMChain(llm=llm, prompt=prompt)
            
            # 调用模型
            response = chain.invoke({"content": content[:2000], "title": title})  # 限制输入长度
            
            result_text = response.get("text", "").strip()
            
            # 尝试解析JSON
            try:
                # 如果返回的不是纯JSON，尝试提取JSON部分
                if not result_text.startswith("{"):
                    import re
                    json_match = re.search(r'({.*})', result_text, re.DOTALL)
                    if json_match:
                        result_text = json_match.group(1)
                
                result = json.loads(result_text)
                
                # 确保结果包含必要的字段
                if "summary" not in result:
                    result["summary"] = ""
                if "is_tech" not in result:
                    result["is_tech"] = False
                
                logger.info(f"生成的摘要: {result['summary']}, 科技相关: {result['is_tech']}")
                
                # 如果启用缓存，将结果保存到缓存
                if use_cache and content_hash:
                    summary_cache = load_summary_cache()
                    summary_cache[content_hash] = result
                    save_summary_cache(summary_cache)
                
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回文本作为摘要
                logger.warning(f"JSON解析失败，使用原始文本: {result_text}")
                result = {"summary": result_text[:50], "is_tech": False}
                
                # 如果启用缓存，将结果保存到缓存
                if use_cache and content_hash:
                    summary_cache = load_summary_cache()
                    summary_cache[content_hash] = result
                    save_summary_cache(summary_cache)
                
                return result
        
        except Exception as e:
            logger.error(f"调用腾讯混元模型失败: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break
    
    return {"summary": "", "is_tech": False}

def summarize_with_hunyuan(hotspots, api_key, max_retries=3, tech_only=False):
    """
    使用腾讯混元模型对热点进行汇总归类，支持重试
    根据tech_only参数使用不同的prompt
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 简化输入数据，只传递必要信息，但包含摘要
            simplified_hotspots = []
            for idx, item in enumerate(hotspots):
                source_name = item.get('source', 'unknown')
                simplified_hotspots.append({
                    "id": idx,
                    "title": item['title'],
                    "source": source_name,
                    "summary": item.get('summary', '')  # 添加摘要信息
                })
            
            # 转换为JSON格式的输入
            hotspot_json = json.dumps(simplified_hotspots, ensure_ascii=False)
            
            # 根据tech_only参数选择不同的prompt
            if tech_only:
                prompt = f"""
                以下是今日科技热点信息列表（包含新闻和社交媒体帖子，JSON格式），部分条目包含内容摘要：
                {hotspot_json}
                请总结出10条最重要的AI相关科技新闻，去除重复和无关内容。如果AI相关数量不足允许补充其他热点科技新闻。
                重点关注最新发布的AI技术、模型或者产品等，相关新闻在返回的结果排序中需要前置；公众号的文章权重更高，其余结果按重要性排序。
                你需要将相似的新闻合并为一条，并提供一个直观简洁的中文标题，需要讲清楚新闻内容不要太泛化（不超过30个字）。
                同时，也请关注来自 Twitter 等社交媒体源 (source: Twitter) 的重要信息，特别是关于最新 AI 技术突破、模型发布或重要行业及AI产品动态的帖子，它们同样具有很高的价值。
                相关新闻的ID列表最多选择其中3条，取最重要和直观的，超过数量不需要全部给出。
                请特别注意，如果同一个账号在多个平台发布相同的内容，或不同平台的新闻标题相似度极高，请过滤掉重复条目，仅需列出1条即可。
                如果有摘要信息，请参考摘要提供更准确的标题。
                
                请以JSON格式返回结果，格式如下：
                ```json
                [
                  {{
                    "title": "热点标题",
                    "related_ids": [相关热点的ID列表]
                  }},
                  ...
                ]
                ```
                
                只返回JSON数据，不要有任何额外说明。
                """
            else:
                prompt = f"""
                以下是今日热点信息列表（包含新闻和社交媒体帖子，JSON格式），部分条目包含内容摘要：
                {hotspot_json}
                请总结出10条最重要的热点新闻，优先选择科技和AI相关新闻，但也要包含其他领域（如社会、娱乐、体育等）的重要新闻，去除重复内容。
                重点关注最新发布的AI技术、模型或者产品等，相关新闻在返回的结果排序中需要前置；公众号的文章权重更高，其余结果按重要性排序。
                你需要将相似的新闻合并为一条，并提供一个直观简洁的中文标题，需要讲清楚新闻内容不要太泛化（不超过30个字）。
                同时，也请关注来自 Twitter 等社交媒体源 (source: Twitter) 的重要信息，特别是关于最新 AI 技术突破、模型发布或重要行业及AI产品动态的帖子，它们同样具有很高的价值。
                相关新闻的ID列表最多选择其中3条，取最重要和直观的，超过数量不需要全部给出。
                请特别注意，如果同一个账号在多个平台发布相同的内容，或不同平台的新闻标题相似度极高，请过滤掉重复条目，仅需列出1条即可。
                如果有摘要信息，请参考摘要提供更准确的标题。
                
                请以JSON格式返回结果，格式如下：
                ```json
                [
                  {{
                    "title": "热点标题",
                    "related_ids": [相关热点的ID列表]
                  }},
                  ...
                ]
                ```
                
                只返回JSON数据，不要有任何额外说明。
                """
            
            # 创建LLM实例
            llm = ChatOpenAI(
                model="hunyuan-lite",
                temperature=0.3,
                api_key=api_key,
                max_tokens=2000,
                base_url="https://api.hunyuan.cloud.tencent.com/v1"
            )
            
            # 创建提示模板
            prompt_template = PromptTemplate(
                input_variables=["prompt"],
                template="{prompt}"
            )
            
            # 创建LLMChain
            chain = LLMChain(llm=llm, prompt=prompt_template)
            
            # 调用模型
            response = chain.invoke({"prompt": prompt})
            result_text = response.get("text", "").strip()
            
            # 添加调试信息
            print(f"混元模型返回的原始文本: {result_text[:500]}...")
            logger.info(f"混元模型返回的原始文本长度: {len(result_text)}")
            
            # 尝试解析JSON
            try:
                # 如果返回的不是纯JSON，尝试提取JSON部分
                if not result_text.startswith("["):
                    import re
                    json_match = re.search(r'(\[.*\])', result_text, re.DOTALL)
                    if json_match:
                        result_text = json_match.group(1)
                
                result = json.loads(result_text)
                print(f"JSON解析成功，结果类型: {type(result)}, 长度: {len(result) if isinstance(result, list) else 'N/A'}")
                
                # 验证结果格式
                if not isinstance(result, list):
                    raise ValueError("返回结果不是列表格式")
                
                # 转换为最终的总结格式
                summary_lines = []
                print(f"开始处理 {len(result)} 个结果项")
                for i, item in enumerate(result):
                    print(f"处理第 {i+1} 项: {item}")
                    if isinstance(item, dict) and 'title' in item:
                        title = item['title']
                        related_ids = item.get('related_ids', [])
                        print(f"  标题: {title}, 相关ID: {related_ids}")
                        if related_ids:
                            # 获取相关新闻的详细信息
                            related_news = []
                            for news_id in related_ids:
                                if isinstance(news_id, int) and 0 <= news_id < len(hotspots):
                                    news_item = hotspots[news_id]
                                    source_name = news_item.get('source', 'unknown')
                                    related_news.append(f"{source_name}: {news_item['title']}")
                            
                            if related_news:
                                summary_lines.append(f"**{title}**")
                                for news in related_news[:3]:  # 最多显示3条相关新闻
                                    summary_lines.append(f"- {news}")
                                summary_lines.append("")
                            else:
                                summary_lines.append(f"**{title}**")
                                summary_lines.append("")
                        else:
                            summary_lines.append(f"**{title}**")
                            summary_lines.append("")
                
                final_summary = "\n".join(summary_lines)
                print("final_summary:", final_summary)
                logger.info(f"混元模型总结完成，生成了 {len(result)} 条热点")
                return final_summary
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败，尝试使用原始文本: {e}")
                # 如果JSON解析失败，尝试提取有用的信息
                lines = result_text.split('\n')
                summary_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('```') and not line.startswith('{') and not line.startswith('['):
                        if line.startswith('"title"') or line.startswith('title'):
                            # 尝试提取标题
                            title_match = re.search(r'"title":\s*"([^"]+)"', line)
                            if title_match:
                                summary_lines.append(f"**{title_match.group(1)}**")
                            else:
                                summary_lines.append(f"**{line}**")
                        elif line.startswith('-') or line.startswith('•'):
                            summary_lines.append(line)
                        elif len(line) > 10:  # 较长的行可能是标题
                            summary_lines.append(f"**{line}**")
                
                if summary_lines:
                    final_summary = "\n".join(summary_lines)
                    logger.info("使用解析后的文本作为总结")
                    return final_summary
                else:
                    # 如果无法解析，返回原始文本
                    logger.warning("无法解析结果，返回原始文本")
                    return result_text
            
        except Exception as e:
            retry_count += 1
            logger.error(f"混元模型调用失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                time.sleep(2 ** retry_count)  # 指数退避
            else:
                raise Exception(f"混元模型调用失败，已重试 {max_retries} 次: {str(e)}")
    
    raise Exception("混元模型调用失败，已达到最大重试次数")

def main():
    """
    测试 summarize_with_hunyuan 方法的主函数
    """
    import os
    from config.config import HUNYUAN_API_KEY
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 获取混元API密钥
        api_key = HUNYUAN_API_KEY
        
        if not api_key:
            print("错误: 未找到混元API密钥")
            print("请通过以下方式之一设置API密钥：")
            print("1. 在项目根目录创建.env文件，添加: HUNYUAN_API_KEY=your_api_key_here")
            print("2. 设置环境变量: export HUNYUAN_API_KEY=your_api_key_here")
            print("3. 或者直接修改代码中的api_key变量")
            print()
            print("为了测试，你可以临时在代码中设置API密钥")
            # 临时测试用，请替换为你的实际API密钥
            # api_key = "your_actual_api_key_here"
            return
        
        # 测试数据 - 模拟热点新闻（简化版本，便于调试）
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
        
        print("=" * 60)
        print("开始测试 summarize_with_hunyuan 方法")
        print("=" * 60)
        print(f"测试数据包含 {len(test_hotspots)} 条热点新闻")
        print()
        
        # 测试1: 普通模式（包含所有类型新闻）
        print("测试1: 普通模式（包含所有类型新闻）")
        print("-" * 40)
        try:
            result1 = summarize_with_hunyuan(test_hotspots, api_key, max_retries=3, tech_only=False)
            print("结果:")
            print(result1)
            print()
        except Exception as e:
            print(f"测试1失败: {str(e)}")
            print()
        
        # 测试2: 仅科技新闻模式
        print("测试2: 仅科技新闻模式")
        print("-" * 40)
        try:
            result2 = summarize_with_hunyuan(test_hotspots, api_key, max_retries=3, tech_only=True)
            print("结果:")
            print(result2)
            print()
        except Exception as e:
            print(f"测试2失败: {str(e)}")
            print()
        
        print("=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
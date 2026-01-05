#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NVIDIA AI日报信息总结：调用NVIDIA AI对当日热点进行总结
"""

import os
import sys
import json
import time
import logging
import requests
import base64
from datetime import datetime
import traceback

# 添加项目根目录到Python路径，确保模块导入正常工作
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import SOURCE_NAME_MAP
from utils.utils import format_title_for_display

# 配置日志
logger = logging.getLogger(__name__)

def summarize_with_nvidia(hotspots, api_key, model_id=None, max_retries=None, tech_only=False):
    """
    使用NVIDIA AI API对热点进行汇总归类，支持重试
    根据tech_only参数使用不同的prompt
    """
    from config.config import NVIDIA_TIMEOUT, NVIDIA_MAX_RETRIES
    
    if model_id is None:
        model_id = "meta/llama-4-maverick-17b-128e-instruct"  # 默认使用示例中的模型
    
    if max_retries is None:
        max_retries = NVIDIA_MAX_RETRIES

    retry_count = 0
    while retry_count < max_retries:
        try:
            # 简化输入数据，只传递必要信息，但包含摘要
            simplified_hotspots = []
            for idx, item in enumerate(hotspots):
                source_name = SOURCE_NAME_MAP.get(
                    item['source'], item['source'])
                simplified_hotspots.append({
                    "id": idx,
                    "title": item['title'],
                    "source": source_name,
                    "summary": item.get('summary', '')  # 添加摘要信息
                })

            # 将完整数据转换为字典以便后续查找
            hotspot_dict = {idx: item for idx, item in enumerate(hotspots)}

            # 转换为JSON格式的输入
            hotspot_json = json.dumps(simplified_hotspots, ensure_ascii=False)

            # 保存输入的JSON数据，使用相对路径
            save_directory = os.path.join("data", "inputs")
            os.makedirs(save_directory, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%H-%M-%S")
            input_filename = os.path.join(save_directory, f"nvidia_input_{today}_{timestamp}.json")
            with open(input_filename, 'w', encoding='utf-8') as f:
                f.write(hotspot_json)
            logger.info(f"已保存NVIDIA AI输入数据至 {input_filename}")
            
            # 根据tech_only参数选择不同的prompt
            if tech_only:
                prompt = f"""
                以下是今日科技热点信息列表（包含新闻和社交媒体帖子，JSON格式），部分条目包含内容摘要：
                {hotspot_json}
                请总结出10条最重要的科技新闻，优先选择AI相关新闻，去除重复和无关内容。
                重点关注最新发布的AI技术或者模型等，相关新闻在返回的结果排序中需要前置；公众号的文章权重更高，其余结果按重要性排序。
                你需要将相似的新闻合并为一条，并提供一个直观简洁的中文标题，需要讲清楚新闻内容不要太泛化（不超过30个字）。
                同时，也请关注来自 Twitter 等社交媒体源 (source: Twitter) 的重要信息，特别是关于最新 AI 技术突破、模型发布或重要行业动态的帖子，它们同样具有很高的价值。
                相关新闻的ID列表最多选择其中4条，取最典型的，超过数量不需要全部给出。请特别注意，如果同一家媒体在多个渠道发布相同的内容，或新闻标题相似度极高，不要同时选择，则仅需列出1条即可。
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
                你需要将相似的新闻合并为一条，并提供一个直观简洁的中文标题，需要讲清楚新闻内容不要太泛化（不超过30个字）。
                同时，也请关注来自 Twitter 等社交媒体源 (source: Twitter) 的重要信息，特别是关于最新 AI 技术突破、模型发布或重要行业动态的帖子，将它们与新闻同等对待进行筛选和总结。
                相关新闻的ID列表最多选择其中4条，取最典型的，超过数量不需要全部给出。请特别注意，如果同一家媒体在多个渠道发布相同的内容，或新闻标题相似度极高，不要同时选择，则仅需列出1条即可。
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

            # 调用NVIDIA AI API
            stream = False  # Set to True if you want to stream responses
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream" if stream else "application/json"
            }

            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻编辑助手，擅长归纳总结热点新闻。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": stream,
                "top_p": 1.00,
                "frequency_penalty": 0.00,
                "presence_penalty": 0.00
            }

            logger.info(
                f"正在调用NVIDIA AI API，模型: {model_id}，尝试次数: {retry_count + 1}/{max_retries}")
            
            # 添加请求详细信息日志
            logger.info(f"API请求URL: https://integrate.api.nvidia.com/v1/chat/completions")
            logger.info(f"API请求头: {headers}")
            logger.info(f"API请求体: {payload}")
            
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=NVIDIA_TIMEOUT  # 使用配置文件中的超时设置
            )

            # 添加响应详细信息日志
            logger.info(f"API响应状态码: {response.status_code}")
            logger.info(f"API响应头: {response.headers}")
            
            response.raise_for_status()
            
            # Handle streaming vs non-streaming responses
            if stream:
                # For streaming responses, collect all chunks
                json_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            chunk_data = decoded_line[6:]
                            if chunk_data != "[DONE]":
                                chunk_json = json.loads(chunk_data)
                                if "choices" in chunk_json and len(chunk_json["choices"]) > 0:
                                    delta = chunk_json["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    json_response += content
                result = {"choices": [{"message": {"content": json_response}}]}
            else:
                # For non-streaming responses
                result = response.json()
                # Add detailed logging
                logger.info(f"API响应内容: {response.text}")
                logger.info(f"完整API响应: {result}")

                # Check if response contains expected structure
                if "choices" not in result or not result["choices"]:
                    logger.error(f"API响应中缺少 'choices' 字段或为空: {result}")
                    raise ValueError("API响应格式不正确，缺少choices字段")

                # Extract response content
                json_response = result["choices"][0]["message"]["content"]
                
            logger.info(f"API返回的消息内容: {json_response}")

            # 提取JSON部分
            json_str = json_response
            if "```json" in json_response:
                json_str = json_response.split(
                    "```json")[1].split("```")[0].strip()

            # 保存NVIDIA AI的完整响应结果
            output_directory = os.path.join("data", "outputs")
            os.makedirs(output_directory, exist_ok=True)

            # 保存原始响应
            raw_output_filename = os.path.join(
                output_directory, f"nvidia_raw_response_{today}_{timestamp}.json")
            with open(raw_output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存NVIDIA AI原始响应至 {raw_output_filename}")

            # 保存处理后的JSON输出
            output_filename = os.path.join(
                output_directory, f"nvidia_output_{today}_{timestamp}.json")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"已保存NVIDIA AI输出数据至 {output_filename}")

            # 解析JSON
            try:
                news_items = json.loads(json_str)

                # 根据JSON构建最终输出
                formatted_summary = ""
                for index, news in enumerate(news_items[:20]):
                    num = str(index + 1).zfill(2)
                    title = news.get("title", "未知标题")

                    formatted_summary += f"## ** {num} {title} **  \n"

                    # 添加相关链接，使用优化的格式
                    related_ids = news.get("related_ids", [])
                    for news_id in related_ids:
                        if news_id in hotspot_dict:
                            item = hotspot_dict[news_id]
                            source_name = SOURCE_NAME_MAP.get(
                                item['source'], item['source'])
                            item_title = item['title']
                            # 格式化标题，确保长度一致
                            if len(item_title) > 18:
                                item_title = item_title[:15] + "..."

                            # 添加链接
                            formatted_summary += f"- [{item_title}]({item['url']}) `🏷️{source_name}`\n"

                    # 添加空行分隔
                    formatted_summary += "\n"

                # 保存格式化后的摘要内容
                summary_filename = os.path.join(
                    output_directory, f"formatted_summary_{today}_{timestamp}.md")
                with open(summary_filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_summary)
                logger.info(f"已保存格式化摘要至 {summary_filename}")

                return formatted_summary

            except json.JSONDecodeError as e:
                logger.error(f"解析NVIDIA AI返回的JSON失败: {str(e)}")
                logger.error(f"尝试解析的JSON字符串: {json_str}")
                return f"解析NVIDIA AI返回的JSON失败: {str(e)}"

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(
                f"NVIDIA AI API 请求超时，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(5)  # 等待5秒后重试

        except requests.exceptions.HTTPError as e:
            logger.error(f"NVIDIA AI API HTTP错误: {str(e)}")
            logger.error(f"响应内容: {response.text if 'response' in locals() else 'No response object'}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break
                
        except KeyError as e:
            logger.error(f"处理NVIDIA AI响应时缺少键: {str(e)}")
            logger.error(f"完整响应: {result if 'result' in locals() else 'No result object'}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

        except Exception as e:
            logger.error(f"调用NVIDIA AI API时发生错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

    # 如果所有重试都失败，返回前20条热点作为备选
    logger.warning("无法使用NVIDIA AI API归类热点，将使用原始热点")
    fallback = ""
    for i, item in enumerate(hotspots[:10]):
        num = str(i + 1).zfill(2)
        source_name = SOURCE_NAME_MAP.get(item['source'], item['source'])
        item_title = item['title']
        # 格式化标题，确保长度一致
        formatted_title = format_title_for_display(item_title, source_name, 30)
        fallback += f"## ** {num} {item['title']} **  \n"
        fallback += f"- [{item_title}]({item['url']}) `🏷️{source_name}` \n\n"
    return fallback


def refine_markdown_with_nvidia(prompt: str, api_key: str = None, model_id: str = None, max_retries: int = None) -> str:
    """
    使用NVIDIA AI API对内容进行润色
    
    Args:
        prompt: 润色提示词
        api_key: NVIDIA API密钥
        model_id: 模型ID
        max_retries: 最大重试次数
    
    Returns:
        str: 润色后的内容
    """
    from config.config import NVIDIA_API_KEY, NVIDIA_TIMEOUT, NVIDIA_MAX_RETRIES
    
    # 优先使用传入的API密钥，否则使用配置文件中的
    if not api_key:
        api_key = NVIDIA_API_KEY
    
    if not api_key:
        logger.error("未配置NVIDIA_API_KEY，请先设置API密钥")
        return prompt
    
    if model_id is None:
        model_id = "meta/llama-4-maverick-17b-128e-instruct"  # 使用示例中的模型
    
    if max_retries is None:
        max_retries = NVIDIA_MAX_RETRIES

    retry_count = 0
    while retry_count < max_retries:
        try:
            # 准备API请求
            stream = False  # Set to True if you want to stream responses
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream" if stream else "application/json"
            }

            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "你是一个专业的科技新闻编辑，擅长对科技日报内容进行去重、融合和润色。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 50000,
                "stream": stream,
                "top_p": 1.00,
                "frequency_penalty": 0.00,
                "presence_penalty": 0.00
            }

            logger.info(
                f"正在调用NVIDIA AI API进行润色，模型: {model_id}，尝试次数: {retry_count + 1}/{max_retries}")
            
            # 添加请求详细信息日志
            logger.info(f"API请求URL: https://integrate.api.nvidia.com/v1/chat/completions")
            logger.info(f"API请求头: {headers}")
            logger.info(f"API请求体: {payload}")
            
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=NVIDIA_TIMEOUT  # 使用配置文件中的超时设置
            )

            response.raise_for_status()
            
            # Handle streaming vs non-streaming responses
            if stream:
                # For streaming responses, collect all chunks
                refined_content = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            chunk_data = decoded_line[6:]
                            if chunk_data != "[DONE]":
                                chunk_json = json.loads(chunk_data)
                                if "choices" in chunk_json and len(chunk_json["choices"]) > 0:
                                    delta = chunk_json["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    refined_content += content
            else:
                # For non-streaming responses
                result = response.json()
                # Add detailed logging
                logger.info(f"API响应内容: {response.text}")

                # Check if response contains expected structure
                if "choices" in result and len(result["choices"]) > 0:
                    refined_content = result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"API响应中缺少 'choices' 字段或为空: {result}")
                    raise ValueError("API响应格式不正确，缺少choices字段")

            logger.info(f"NVIDIA API润色成功，内容长度: {len(refined_content)} 字符")
            
            # 清理代码块标记和确认语句
            cleaned_content = _clean_markdown_blocks_nvidia(refined_content)
            
            return cleaned_content

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(
                f"NVIDIA AI API 请求超时，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(5)  # 等待5秒后重试

        except requests.exceptions.HTTPError as e:
            logger.error(f"NVIDIA AI API HTTP错误: {str(e)}")
            logger.error(f"响应内容: {response.text if 'response' in locals() else 'No response object'}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break
                
        except KeyError as e:
            logger.error(f"处理NVIDIA AI响应时缺少键: {str(e)}")
            logger.error(f"完整响应: {result if 'result' in locals() else 'No result object'}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

        except Exception as e:
            logger.error(f"调用NVIDIA AI API进行润色时发生错误: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

    # 如果所有重试都失败，返回原始内容
    logger.warning("NVIDIA AI API润色失败，返回原始内容")
    return prompt


def _clean_markdown_blocks_nvidia(content: str) -> str:
    """
    清理代码块标记和确认语句

    Args:
        content: 原始内容

    Returns:
        str: 清理后的内容
    """
    if not content:
        return content

    # 移除开头的 ````
    if content.startswith('````'):
        content = content[4:]  # 移除 ````

    # 移除开头的 ```
    if content.startswith('```'):
        content = content[3:]

    # 移除结尾的 ```
    if content.endswith('```'):
        content = content[:-3]

    # 移除开头的换行符
    content = content.lstrip('\n')

    # 移除结尾的换行符
    content = content.rstrip('\n')

    # 清理确认语句和无关内容
    lines = content.split('\n')
    cleaned_lines = []
    skip_until_markdown = False

    for line in lines:
        # 跳过确认语句
        if any(phrase in line for phrase in [
            "好的，收到！",
            "我将按照您的要求",
            "对提供的科技日报内容进行",
            "深度去重、融合、润色和结构优化",
            "并按照指定的 Markdown 格式输出",
            "好的，我明白了",
            "我来帮您",
            "我将为您",
            "以下是",
            "请查看以下内容",
            "已按要求",
            "已完成",
            "根据您的要求"
        ]):
            continue

        # 如果遇到代码标题，开始保留内容
        if line.strip().startswith('#') or line.strip().startswith('##'):
            skip_until_markdown = False

        # 如果还没有遇到代码标题，跳过空行
        if skip_until_markdown and not line.strip():
            continue

        # 如果遇到代码标题，标记开始保留内容
        if line.strip().startswith('#') or line.strip().startswith('##'):
            skip_until_markdown = True

        if skip_until_markdown or line.strip():
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def main():
    """
    测试NVIDIA AI API集成的主函数
    """
    import os
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 模拟热点数据
    test_hotspots = [
        {
            "title": "OpenAI发布GPT-5模型，性能大幅提升",
            "url": "https://example.com/news1",
            "source": "techcrunch",
            "summary": "OpenAI发布了最新的GPT-5模型，在多个基准测试中表现优异，推理能力和代码生成能力都有显著提升。"
        },
        {
            "title": "谷歌推出新的AI助手Gemini Advanced",
            "url": "https://example.com/news2", 
            "source": "theverge",
            "summary": "谷歌发布了Gemini Advanced，这是一个更强大的AI助手，支持多模态输入和更复杂的推理任务。"
        },
        {
            "title": "微软投资OpenAI 100亿美元",
            "url": "https://example.com/news3",
            "source": "reuters",
            "summary": "微软宣布向OpenAI投资100亿美元，深化AI合作，进一步推进AI技术的商业化应用。"
        },
        {
            "title": "Meta发布新的AI研究论文",
            "url": "https://example.com/news4",
            "source": "arxiv",
            "summary": "Meta发布了一篇关于大规模语言模型训练的新研究论文，提出了更高效的训练方法。"
        },
        {
            "title": "特斯拉自动驾驶技术更新",
            "url": "https://example.com/news5",
            "source": "tesla",
            "summary": "特斯拉发布了最新的自动驾驶技术更新，提升了车辆在复杂路况下的表现。"
        }
    ]
    
    # 从环境变量获取API密钥
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        logger.error("未设置NVIDIA_API_KEY环境变量，请先设置API密钥")
        logger.info("设置方法: export NVIDIA_API_KEY='your_api_key_here'")
        return
    
    logger.info("开始测试NVIDIA AI API集成...")
    logger.info(f"测试数据包含 {len(test_hotspots)} 条热点信息")
    
    try:
        # 测试科技新闻模式
        logger.info("测试科技新闻模式 (tech_only=True)...")
        result_tech = summarize_with_nvidia(
            hotspots=test_hotspots,
            api_key=api_key,
            model_id="meta/llama-4-maverick-17b-128e-instruct",  # Using model from example
            max_retries=2,
            tech_only=True
        )
        
        logger.info("科技新闻模式测试成功!")
        logger.info(f"返回结果长度: {len(result_tech)} 字符")
        logger.info("结果预览:")
        logger.info(result_tech[:500] + "..." if len(result_tech) > 500 else result_tech)
        
        # 测试全领域模式
        logger.info("\n" + "="*50)
        logger.info("测试全领域模式 (tech_only=False)...")
        result_all = summarize_with_nvidia(
            hotspots=test_hotspots,
            api_key=api_key,
            model_id="meta/llama-4-maverick-17b-128e-instruct",  # Using model from example
            max_retries=2,
            tech_only=False
        )
        
        logger.info("全领域模式测试成功!")
        logger.info(f"返回结果长度: {len(result_all)} 字符")
        logger.info("结果预览:")
        logger.info(result_all[:500] + "..." if len(result_all) > 500 else result_all)
        
        logger.info("\n" + "="*50)
        logger.info("所有测试完成!")
        
    except Exception as e:
        logger.error(f"NVIDIA AI API测试失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
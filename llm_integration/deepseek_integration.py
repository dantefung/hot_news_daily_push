#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
deepseek日报信息总结：调用deepseek对当日热点进行总结
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from config.config import SOURCE_NAME_MAP
from utils.utils import format_title_for_display

# 配置日志
logger = logging.getLogger(__name__)

def summarize_with_deepseek(hotspots, api_key, api_url=None, model_id=None, max_retries=3, tech_only=False):
    """
    使用Deepseek API对热点进行汇总归类，支持重试
    根据tech_only参数使用不同的prompt
    """
    if api_url is None:
        api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    if model_id is None:
        model_id = "ep-20250307234946-b2znq"

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
            input_filename = os.path.join(save_directory, f"deepseek_input_{today}_{timestamp}.json")
            with open(input_filename, 'w', encoding='utf-8') as f:
                f.write(hotspot_json)
            logger.info(f"已保存Deepseek输入数据至 {input_filename}")
            
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

            # 调用Deepseek API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻编辑助手，擅长归纳总结热点新闻。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }

            logger.info(
                f"正在调用 Deepseek API，尝试次数: {retry_count + 1}/{max_retries}")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            # 提取回复内容
            json_response = result["choices"][0]["message"]["content"]

            # 提取JSON部分
            json_str = json_response
            if "```json" in json_response:
                json_str = json_response.split(
                    "```json")[1].split("```")[0].strip()

            # 保存Deepseek的完整响应结果
            output_directory = os.path.join("data", "outputs")
            os.makedirs(output_directory, exist_ok=True)

            # 保存原始响应
            raw_output_filename = os.path.join(
                output_directory, f"deepseek_raw_response_{today}_{timestamp}.json")
            with open(raw_output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存Deepseek原始响应至 {raw_output_filename}")

            # 保存处理后的JSON输出
            output_filename = os.path.join(
                output_directory, f"deepseek_output_{today}_{timestamp}.json")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"已保存Deepseek输出数据至 {output_filename}")

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
                            # 新增：如果有配图，插入图片
                            if item.get('image_url'):
                                formatted_summary += f"  ![]({item['image_url']})\n"
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
                logger.error(f"解析Deepseek返回的JSON失败: {str(e)}")
                return f"解析Deepseek返回的JSON失败: {str(e)}"

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(
                f"Deepseek API 请求超时，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(5)  # 等待5秒后重试

        except Exception as e:
            logger.error(f"调用Deepseek API时发生错误: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

    # 如果所有重试都失败，返回前20条热点作为备选
    logger.warning("无法使用Deepseek API归类热点，将使用原始热点")
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


def refine_markdown_with_deepseek(prompt: str, api_key: str = None, api_url: str = None, model_id: str = None, max_retries: int = 3) -> str:
    """
    使用Deepseek API对文本内容进行润色
    
    Args:
        prompt: 润色提示词
        api_key: Deepseek API密钥
        api_url: API端点URL
        model_id: 模型ID
        max_retries: 最大重试次数
    
    Returns:
        str: 润色后的内容
    """
    from config.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL_ID
    
    # 优先使用传入的参数，否则使用配置文件中的
    if not api_key:
        api_key = DEEPSEEK_API_KEY
    if not api_url:
        api_url = DEEPSEEK_API_URL or "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    if not model_id:
        model_id = DEEPSEEK_MODEL_ID or "ep-20250307234946-b2znq"
    
    if not api_key:
        logger.error("未配置DEEPSEEK_API_KEY，请先设置API密钥")
        return prompt

    retry_count = 0
    while retry_count < max_retries:
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # 构建请求体
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "你是一个专业的科技新闻编辑，擅长对科技日报内容进行去重、融合和润色。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 50000
            }

            logger.info(f"正在调用 Deepseek API 进行润色，模型: {model_id}，端点: {api_url}，尝试次数: {retry_count + 1}/{max_retries}")
            
            # 调用Deepseek API
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            # 提取回复内容
            refined_content = result["choices"][0]["message"]["content"]

            logger.info(f"Deepseek API润色成功，内容长度: {len(refined_content)} 字符")
            
            # 清理代码块标记和确认语句
            cleaned_content = _clean_markdown_blocks_deepseek(refined_content)
            
            return cleaned_content

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(
                f"Deepseek API 请求超时，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(5)  # 等待5秒后重试

        except Exception as e:
            logger.error(f"调用Deepseek API进行润色时发生错误: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

    # 如果所有重试都失败，返回原始内容
    logger.error(f"Deepseek API润色失败，已达到最大重试次数 {max_retries}")
    return prompt


def _clean_markdown_blocks_deepseek(content: str) -> str:
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

        # 如果遇到代码块，开始保留内容
        if line.startswith('``'):
            skip_until_markdown = False

        # 如果还没有遇到代码块，跳过空行
        if skip_until_markdown and not line.strip():
            continue

        # 如果遇到代码块，标记开始保留内容
        if line.startswith('``'):
            skip_until_markdown = True

        if skip_until_markdown or line.strip():
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
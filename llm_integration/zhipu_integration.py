#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智谱清言日报信息总结：调用智谱清言对当日热点进行总结
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

def summarize_with_zhipu(hotspots, api_key, model_id=None, max_retries=3, tech_only=False):
    """
    使用智谱清言 API对热点进行汇总归类，支持重试
    根据tech_only参数使用不同的prompt
    """
    if model_id is None:
        model_id = "glm-4.5-flash"

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
            input_filename = os.path.join(save_directory, f"zhipu_input_{today}_{timestamp}.json")
            with open(input_filename, 'w', encoding='utf-8') as f:
                f.write(hotspot_json)
            logger.info(f"已保存智谱清言输入数据至 {input_filename}")
            
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

            # 调用智谱清言 API
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
                f"正在调用智谱清言 API，尝试次数: {retry_count + 1}/{max_retries}")
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
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

            # 保存智谱清言的完整响应结果
            output_directory = os.path.join("data", "outputs")
            os.makedirs(output_directory, exist_ok=True)

            # 保存原始响应
            raw_output_filename = os.path.join(
                output_directory, f"zhipu_raw_response_{today}_{timestamp}.json")
            with open(raw_output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存智谱清言原始响应至 {raw_output_filename}")

            # 保存处理后的JSON输出
            output_filename = os.path.join(
                output_directory, f"zhipu_output_{today}_{timestamp}.json")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"已保存智谱清言输出数据至 {output_filename}")

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
                logger.error(f"解析智谱清言返回的JSON失败: {str(e)}")
                return f"解析智谱清言返回的JSON失败: {str(e)}"

        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(
                f"智谱清言 API 请求超时，正在重试 ({retry_count}/{max_retries})...")
            time.sleep(5)  # 等待5秒后重试

        except Exception as e:
            logger.error(f"调用智谱清言 API时发生错误: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"5秒后重试 ({retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                break

    # 如果所有重试都失败，返回前20条热点作为备选
    logger.warning("无法使用智谱清言 API归类热点，将使用原始热点")
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


def main():
    """
    测试智谱清言API集成的主函数
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
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        logger.error("未设置ZHIPU_API_KEY环境变量，请先设置API密钥")
        logger.info("设置方法: export ZHIPU_API_KEY='your_api_key_here'")
        return
    
    logger.info("开始测试智谱清言API集成...")
    logger.info(f"测试数据包含 {len(test_hotspots)} 条热点信息")
    
    try:
        # 测试科技新闻模式
        logger.info("测试科技新闻模式 (tech_only=True)...")
        result_tech = summarize_with_zhipu(
            hotspots=test_hotspots,
            api_key=api_key,
            model_id="glm-4.5-flash",
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
        result_all = summarize_with_zhipu(
            hotspots=test_hotspots,
            api_key=api_key,
            model_id="glm-4.5-flash",
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
        logger.error(f"智谱清言API测试失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
后置处理组件：下载远程文件、融合内容并让AI去重润色
"""

import os
import re
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# 导入扩展点接口
from processor import PostProcessorInterface
from config.config import REFINED_DRAFT_COUNT

# 配置日志
logger = logging.getLogger(__name__)

# 定义代理配置
# proxies = {
#     "http": "http://127.0.0.1:1080",
#     "https": "http://127.0.0.1:1080"
# }
proxies = None

# 检查是否配置了代理
use_proxies = bool(proxies)


class PostMergeRefineProcessor(PostProcessorInterface):
    """后置处理组件：融合和润色"""

    def __init__(self, llm_integration=None, enable_enhanced_processing=True):
        """
        初始化后置处理器

        Args:
            llm_integration: LLM集成模块，用于AI润色
            enable_enhanced_processing: 是否启用增强处理功能
        """
        self.llm_integration = llm_integration
        self.enable_enhanced_processing = enable_enhanced_processing
        self.today = datetime.now().strftime('%Y-%m-%d')

    def get_name(self) -> str:
        """获取处理器名称"""
        return "PostMergeRefineProcessor"

    def get_priority(self) -> int:
        """获取处理器优先级"""
        return 10  # 较高优先级

    def is_enabled(self, context: Dict[str, Any]) -> bool:
        """检查处理器是否启用"""
        return context.get('enable_post_process', True)

    def download_remote_md_files(self) -> Tuple[str, str]:
        """
        下载远程markdown文件

        Returns:
            Tuple[str, str]: 两个远程文件的内容
        """
        mdfile = f"{self.today}.md"
        urls = [
            f"https://raw.githubusercontent.com/justlovemaki/CloudFlare-AI-Insight-Daily/book/daily/{mdfile}",
            f"https://raw.githubusercontent.com/dantefung/daily-tech-articles/book/daily/{mdfile}"
        ]

        contents = []
        for i, url in enumerate(urls):
            try:
                logger.info(f"正在下载远程文件 {i+1}: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                content = response.text
                logger.info(f"成功下载文件 {i+1}，内容长度: {len(content)} 字符")
                contents.append(content)
            except requests.exceptions.RequestException as e:
                logger.warning(f"下载文件 {i+1} 失败: {url}，错误: {e}")
                contents.append("")  # 使用空字符串作为占位符
            except Exception as e:
                logger.error(f"下载文件 {i+1} 时发生未知错误: {e}")
                contents.append("")

        return contents[0], contents[1]

    def read_local_summary(self, summary_path: str) -> str:
        """
        读取本地summary文件

        Args:
            summary_path: 本地summary文件路径

        Returns:
            str: 文件内容
        """
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(
                f"成功读取本地summary文件: {summary_path}，内容长度: {len(content)} 字符")
            return content
        except Exception as e:
            logger.error(f"读取本地summary文件失败: {summary_path}，错误: {e}")
            return ""

    def merge_contents(self, local_summary: str, remote1: str, remote2: str) -> str:
        """
        合并三个文件的内容

        Args:
            local_summary: 本地summary内容
            remote1: 远程文件1内容
            remote2: 远程文件2内容

        Returns:
            str: 合并后的内容
        """
        # 直接合并内容，不添加来源标识标题
        merged_content = f"""{local_summary}

{remote1}

{remote2}
"""

        logger.info(f"合并内容完成，总长度: {len(merged_content)} 字符")
        return merged_content

    def ai_refine_content(self, merged_content: str) -> str:
        """
        使用AI对合并内容进行去重和润色，并生成SEO标题

        Args:
            merged_content: 合并后的内容

        Returns:
            str: 润色后的内容（带SEO标题）
        """
        if not self.llm_integration:
            logger.warning("未配置LLM集成，跳过AI润色")
            return merged_content

        try:
            # 构建更详细的AI润色prompt
            prompt = f"""
你是一位专业的科技新闻编辑，请对以下合并的科技日报内容进行深度去重、融合和润色，并按照指定的格式输出。

**重要：请直接输出markdown内容，不要添加任何确认语句、解释或前言。**

{merged_content}

## 处理要求：

### 1. 去重策略
- 识别并合并完全相同的新闻条目
- 识别并合并报道同一事件的相似新闻
- 识别并合并同一技术或产品的不同角度报道
- 保留最新、最详细、最权威的版本

### 2. 内容融合
- 将相似新闻的不同信息点合并
- 补充缺失的重要信息
- 统一报道角度和表述方式
- 保持信息的完整性和准确性

### 3. 内容润色
- 优化标题，使其更吸引人且准确
- 改进描述，使其更清晰易懂
- 统一语言风格，保持专业性
- 确保逻辑清晰，层次分明

### 4. 结构优化
- 按重要性和时效性排序
- 使用清晰的markdown格式
- 添加适当的分类和分组
- 保持原文的链接信息

### 5. 质量保证
- 确保每条新闻都有明确的标题和描述
- 验证链接的有效性
- 保持内容的时效性
- 确保信息的准确性和可靠性

### 6. 摘要换行要求
- **请特别注意：AI内容摘要（即“AI内容摘要”代码块内的内容）如果过长，请自动合理换行，建议每行不超过40个中文字符，英文不强制换行。**

### 7. SEO标题生成
- **首要任务：** 从今日内容中，**精准定位最吸引眼球、最具争议性或最重大的新闻事件**作为标题核心。
- **创作目标：** 生成一个10字以内、**极具吸引力、能引发好奇心**的SEO友好中文标题。
- **标题技巧：**
    - **提炼“噱头”：** 抓住最劲爆的点，如“惊天漏洞”、“再爆争议”、“黑科技发布”、“免费用”等。
    - **制造悬念或冲突：** 如“AI巨头互撕”、“...或成最大赢家”、“...时代终结？”。
    - **突出“最”或“首次”：** 找到文中的“最强”、“首次公开”等突破性信息。
- **确保相关：** 标题必须源于正文，不能凭空捏造。
- **风格多样：** 在确保“吸睛”和“相关”的前提下，每次生成时请变换风格角度，避免重复。
- 直接以“SEO标题: xxx”单独一行输出在最前面。

## 输出格式要求：
**请直接输出以下格式的markdown内容，不要添加任何其他文字：**

SEO标题: xxx

# AI科技日报-2025-07-21

> 🤖 AI科技日报 | ⏰ 每日精选 | 🌐 全球资讯 | 🔬 前沿探索 | 💡 深度分析 | 🛠️ 开源创新 | 🚀 未来展望 | [🌍 网页版↗️]

### **AI内容摘要**

```
[用2-3句话总结今日最重要的AI相关新闻要点]
```

### AI前沿研究

[按重要性排序，每条新闻用1-2段话描述，包含：
- 研究机构/团队名称（用**加粗**）
- 技术/方法名称（用**加粗**）
- 技术原理和优势
- 相关链接（论文地址、项目地址等）
- 使用emoji增强可读性]

### 开源TOP项目

[按重要性排序，每条项目用1-2段话描述，包含：
- 项目名称（用**加粗**）
- 项目简介和特色功能
- GitHub星数（如适用）
- 项目地址链接
- 使用emoji增强可读性]

### 社媒分享

[按重要性排序，每条分享用1-2段话描述，包含：
- 分享者姓名（用**加粗**）
- 核心观点和见解
- 相关链接
- 图片链接（如适用）
- 使用emoji增强可读性]

---

**请确保：**
1. 内容去重彻底，避免重复报道
2. 语言生动有趣，使用emoji增强可读性
3. 保持原文的链接信息
4. 按重要性合理排序
5. 格式完全符合上述模板
6. **直接输出markdown内容，不要添加任何确认语句或解释**
"""
            # 保存prompt到data/outputs目录
            import os
            from datetime import datetime
            os.makedirs("data/outputs", exist_ok=True)
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            prompt_path = f"data/outputs/llm_prompt_{timestamp_str}.txt"
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            logger.info(f"已保存大模型请求prompt到: {prompt_path}")

            # 调用LLM进行润色
            refined_content = self.llm_integration.refine_markdown(prompt)
            logger.info("AI润色完成")

            # 保存响应到data/outputs目录
            response_path = f"data/outputs/llm_response_{timestamp_str}.md"
            print("保存响应到data/outputs目录", response_path)
            with open(response_path, 'w', encoding='utf-8') as f:
                f.write(refined_content)
            logger.info(f"已保存大模型响应到: {response_path}")

            # 自动提取SEO标题并插入到Markdown一级标题
            import re
            seo_title = None
            lines = refined_content.splitlines()
            for i, line in enumerate(lines):
                m = re.match(r"SEO标题[:：]\s*(.+)", line)
                if m:
                    seo_title = m.group(1).strip()
                    # 查找下一个一级标题
                    for j in range(i+1, len(lines)):
                        if lines[j].startswith("# AI科技日报-"):
                            lines[j] = f"# AI科技日报-2025-07-21 {seo_title}"
                            break
                    # 移除SEO标题行
                    lines.pop(i)
                    break
            refined_content = "\n".join(lines)
            return refined_content

        except Exception as e:
            logger.error(f"AI润色失败: {e}")
            return merged_content

    def preprocess_content_for_ai(self, merged_content: str) -> str:
        merged_content = merged_content.replace(
            "[访问网页版↗️](https://ai.hubtoday.app/)", "")
        return merged_content

    def validate_refined_content(self, refined_content: str) -> Tuple[bool, str]:
        """
        验证润色后的内容质量

        Args:
            refined_content: 润色后的内容

        Returns:
            Tuple[bool, str]: (是否通过验证, 验证信息)
        """
        try:
            if not refined_content or len(refined_content.strip()) < 100:
                return False, "内容过短或为空"

            # 检查是否包含必要的结构（新格式）
            required_sections = ["AI内容摘要", "AI前沿研究", "开源TOP项目", "社媒分享"]
            missing_sections = []

            for section in required_sections:
                if section not in refined_content:
                    missing_sections.append(section)

            if missing_sections:
                return False, f"缺少必要的章节: {', '.join(missing_sections)}"

            # 检查markdown格式
            if not refined_content.startswith("##") and not refined_content.startswith("#"):
                return False, "内容不是有效的markdown格式"

            # 检查是否包含标题
            if "科技日报" not in refined_content:
                return False, "缺少日报标题"

            # 检查内容长度
            if len(refined_content) < 500:
                return False, "内容长度不足，可能润色不完整"

            # 检查是否包含摘要部分
            if "### **AI内容摘要**" not in refined_content:
                return False, "缺少AI内容摘要部分"

            return True, "内容质量验证通过"

        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"

    def save_refined_content(self, refined_content: str, output_path: str) -> bool:
        """
        保存润色后的内容

        Args:
            refined_content: 润色后的内容
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        try:
            # 直接保存，不再本地换行
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(refined_content)

            logger.info(f"润色后的内容已保存到: {output_path}")
            return True

        except Exception as e:
            logger.error(f"保存润色内容失败: {output_path}，错误: {e}")
            return False

    def process(self, summary: str, context: Dict[str, Any]) -> str:
        """
        处理摘要内容（符合PostProcessorInterface接口）

        Args:
            summary: 原始摘要内容
            context: 处理上下文

        Returns:
            str: 处理后的摘要内容（主推送用第一份）
        """
        try:
            import tempfile
            draft_count = context.get(
                'refined_draft_count', REFINED_DRAFT_COUNT)
            refined_summaries = []
            output_paths = []
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(summary)
                temp_summary_path = temp_file.name
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = os.path.join("data", "outputs")
            os.makedirs(output_dir, exist_ok=True)
            for i in range(1, draft_count + 1):
                diff_hint = ""
                if i > 1:
                    diff_hint = ("\n\n【差异化要求】请用与上一稿明显不同的表达方式、结构或角度重写，"
                                 "可以适当调整内容顺序、突出不同要点，避免与上一稿重复。风格可更简洁、详细、口语化或学术化等。")
                output_path = os.path.join(
                    output_dir, f"refined_summary_{timestamp_str}_draft_{i}.md")
                output_paths.append(output_path)
                success = self._process_internal(
                    temp_summary_path, output_path, context.get('summary_model', 'gemini'), diff_hint)
                if success:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        refined_summary = f.read()
                    logger.info(
                        f"后置处理成功，处理后摘要长度: {len(refined_summary)} (draft {i})")
                    refined_summaries.append(refined_summary)
                else:
                    logger.warning(f"后置处理失败（draft {i}），返回原始summary")
                    refined_summaries.append(summary)
            # 写入 context
            context['refined_summaries'] = refined_summaries
            # 返回第一份（主推送用）
            return refined_summaries[0] if refined_summaries else summary
        except Exception as e:
            logger.error(f"后置处理失败: {str(e)}")
            return summary

    def _process_internal(self, summary_path: str, output_path: str, llm_type: str = "gemini", diff_hint: str = "") -> bool:
        """
        内部处理方法（增强版，包含智能预处理）

        Args:
            summary_path: 本地summary文件路径
            output_path: 输出文件路径
            llm_type: LLM类型
            diff_hint: 差异化提示

        Returns:
            bool: 处理是否成功
        """
        try:
            logger.info("开始执行增强版后置处理流程")

            # 初始化LLM集成（如果还没有初始化）
            if not self.llm_integration:
                logger.info(f"初始化LLM集成，类型: {llm_type}")
                try:
                    self.llm_integration = create_llm_adapter(llm_type)
                    logger.info("LLM集成初始化成功")
                except Exception as e:
                    logger.error(f"LLM集成初始化失败: {e}")
                    # 继续执行，但不进行AI润色

            # 1. 下载远程文件
            remote1, remote2 = self.download_remote_md_files()

            # 2. 读取本地summary
            local_summary = self.read_local_summary(summary_path)

            # 3. 合并内容
            merged_content = self.merge_contents(
                local_summary, remote1, remote2)

            # 4. 智能预处理（新增）
            if self.enable_enhanced_processing:
                logger.info("开始智能预处理...")
                preprocessed_content = self.preprocess_content_for_ai(
                    merged_content)

                # 保存预处理结果用于调试
                outputs_dir = os.path.join("data", "outputs")
                os.makedirs(outputs_dir, exist_ok=True)
                timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                outputs_path = os.path.join(
                    outputs_dir, f"preprocessed_{timestamp_str}.md")
                with open(outputs_path, 'w', encoding='utf-8') as f:
                    f.write(preprocessed_content)
                logger.info(f"预处理结果已保存到: {outputs_path}")

                # 5. AI润色（使用预处理后的内容+差异化提示）
                logger.info("开始AI润色...")
                refined_content = self.ai_refine_content(
                    preprocessed_content + diff_hint)
            else:
                # 使用传统方式
                logger.info("使用传统方式处理...")

            # 7. 保存结果
            success = self.save_refined_content(refined_content, output_path)

            if success:
                logger.info("增强版后置处理流程完成")
            else:
                logger.error("增强版后置处理流程失败")

            return success

        except Exception as e:
            logger.error(f"增强版后置处理流程发生异常: {e}")
            return False


# LLM集成适配器
class LLMIntegrationAdapter:
    """LLM集成适配器，统一不同LLM的接口"""

    def __init__(self, llm_type="gemini", **kwargs):
        """
        初始化LLM适配器

        Args:
            llm_type: LLM类型 ("gemini", "deepseek", "hunyuan")
            **kwargs: LLM配置参数
        """
        self.llm_type = llm_type
        self.config = kwargs
        self._init_llm()

    def _init_llm(self):
        """初始化LLM"""
        try:
            if self.llm_type == "gemini":
                from llm_integration.gemini_integration import summarize_with_gemini
                self.llm_func = summarize_with_gemini
            elif self.llm_type == "deepseek":
                from llm_integration.deepseek_integration import summarize_with_deepseek
                self.llm_func = summarize_with_deepseek
            elif self.llm_type == "hunyuan":
                from llm_integration.hunyuan_integration import summarize_with_hunyuan
                self.llm_func = summarize_with_hunyuan
            else:
                raise ValueError(f"不支持的LLM类型: {self.llm_type}")

            logger.info(f"LLM适配器初始化成功，类型: {self.llm_type}")

        except Exception as e:
            logger.error(f"LLM适配器初始化失败: {e}")
            self.llm_func = None

    def refine_markdown(self, prompt: str) -> str:
        """
        润色markdown内容

        Args:
            prompt: 润色提示词

        Returns:
            str: 润色后的内容
        """
        if not self.llm_func:
            logger.error("LLM函数未初始化")
            return prompt

        try:
            # 直接调用LLM进行润色，不依赖现有的总结函数
            if self.llm_type == "gemini":
                return self._refine_with_gemini(prompt)
            elif self.llm_type == "deepseek":
                return self._refine_with_deepseek(prompt)
            elif self.llm_type == "hunyuan":
                return self._refine_with_hunyuan(prompt)
            else:
                logger.error(f"不支持的LLM类型: {self.llm_type}")
                return prompt

        except Exception as e:
            logger.error(f"LLM润色失败: {e}")
            return prompt

    def _refine_with_gemini(self, prompt: str) -> str:
        """使用Gemini进行润色"""
        import requests
        from config.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

        try:
            # 使用指定的代理URL
            base_url = "https://api-proxy.me/gemini"
            api_url = f"{base_url.rstrip('/')}/v1beta/models/{GEMINI_MODEL_NAME}:generateContent"

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY
            }

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 50000
                }
            }

            logger.info(
                f"正在调用 Gemini API 进行润色，模型: {GEMINI_MODEL_NAME}，端点: {api_url}")

            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60,
                proxies=proxies if use_proxies else None  # 根据条件使用代理
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Gemini API 润色响应状态码: {response.status_code}")

            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    content = candidate["content"]["parts"][0].get("text", "")
                    # 清理markdown代码块标记
                    return self._clean_markdown_blocks(content)

            return "Gemini润色失败：无法解析响应"

        except Exception as e:
            logger.error(f"Gemini润色失败: {e}")
            return f"Gemini润色失败: {e}"

    def _refine_with_deepseek(self, prompt: str) -> str:
        """使用DeepSeek进行润色"""
        import requests
        from config.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL_ID

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }

            payload = {
                "model": DEEPSEEK_MODEL_ID,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 50000
            }

            logger.info(
                f"正在调用 DeepSeek API 进行润色，模型: {DEEPSEEK_MODEL_ID}，端点: {DEEPSEEK_API_URL}")

            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
                proxies=proxies if use_proxies else None  # 根据条件使用代理
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"DeepSeek API 润色响应状态码: {response.status_code}")

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                # 清理markdown代码块标记
                return self._clean_markdown_blocks(content)

            return "DeepSeek润色失败：无法解析响应"

        except Exception as e:
            logger.error(f"DeepSeek润色失败: {e}")
            return f"DeepSeek润色失败: {e}"

    def _refine_with_hunyuan(self, prompt: str) -> str:
        """使用混元进行润色"""
        import requests
        from config.config import HUNYUAN_API_KEY

        try:
            # 混元API配置
            api_url = "https://hunyuan.tencentcloudapi.com/"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {HUNYUAN_API_KEY}"
            }

            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 50000
            }

            logger.info(f"正在调用混元 API 进行润色，端点: {api_url}")

            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60,
                proxies=proxies if use_proxies else None  # 根据条件使用代理
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"混元 API 润色响应状态码: {response.status_code}")

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                # 清理markdown代码块标记
                return self._clean_markdown_blocks(content)

            return "混元润色失败：无法解析响应"

        except Exception as e:
            logger.error(f"混元润色失败: {e}")
            return f"混元润色失败: {e}"

    def _clean_markdown_blocks(self, content: str) -> str:
        """
        清理markdown代码块标记和确认语句

        Args:
            content: 原始内容

        Returns:
            str: 清理后的内容
        """
        if not content:
            return content

        # 移除开头的 ```markdown
        if content.startswith('```markdown'):
            content = content[12:]  # 移除 ```markdown

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
                "请查看以下内容"
            ]):
                continue

            # 如果遇到markdown标题，开始保留内容
            if line.strip().startswith('#') or line.strip().startswith('##'):
                skip_until_markdown = False

            # 如果还没有遇到markdown标题，跳过空行
            if skip_until_markdown and not line.strip():
                continue

            # 如果遇到markdown标题，标记开始保留内容
            if line.strip().startswith('#') or line.strip().startswith('##'):
                skip_until_markdown = True

            if skip_until_markdown or line.strip():
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _json_to_markdown(self, json_data: List[dict]) -> str:
        """
        将JSON格式的结果转换为markdown格式

        Args:
            json_data: JSON格式的数据

        Returns:
            str: markdown格式的内容
        """
        markdown_lines = []
        markdown_lines.append(f"# 科技日报 - {self.today}")
        markdown_lines.append("")

        for i, item in enumerate(json_data, 1):
            title = item.get('title', '')
            related_ids = item.get('related_ids', [])

            markdown_lines.append(f"## ** {i:02d} {title} **")
            if related_ids:
                markdown_lines.append(f"- 相关ID: {related_ids}")
            markdown_lines.append("")

        return "\n".join(markdown_lines)


def create_llm_adapter(llm_type: str = "gemini") -> LLMIntegrationAdapter:
    """
    创建LLM适配器

    Args:
        llm_type: LLM类型

    Returns:
        LLMIntegrationAdapter: LLM适配器实例
    """
    from config.config import GEMINI_API_KEY, DEEPSEEK_API_KEY, HUNYUAN_API_KEY

    if llm_type == "gemini":
        return LLMIntegrationAdapter(
            llm_type="gemini",
            api_key=GEMINI_API_KEY
        )
    elif llm_type == "deepseek":
        return LLMIntegrationAdapter(
            llm_type="deepseek",
            api_key=DEEPSEEK_API_KEY
        )
    elif llm_type == "hunyuan":
        return LLMIntegrationAdapter(
            llm_type="hunyuan",
            api_key=HUNYUAN_API_KEY
        )
    else:
        raise ValueError(f"不支持的LLM类型: {llm_type}")


def post_process_summary(summary_path: str, output_path: str, llm_type: str = "gemini") -> bool:
    """
    后置处理summary文件

    Args:
        summary_path: 本地summary文件路径
        output_path: 输出文件路径
        llm_type: LLM类型

    Returns:
        bool: 处理是否成功
    """
    try:
        # 创建LLM适配器
        llm_adapter = create_llm_adapter(llm_type)

        # 创建后置处理器
        processor = PostMergeRefineProcessor(llm_integration=llm_adapter)

        # 执行处理
        return processor.process(summary_path, output_path)

    except Exception as e:
        logger.error(f"后置处理失败: {e}")
        return False


if __name__ == "__main__":
    # 测试用例
    summary_path = "data/outputs/formatted_summary_2025-07-11_01-21-02.md"
    output_path = "data/outputs/final_refined_summary.md"

    success = post_process_summary(summary_path, output_path, "gemini")

    if success:
        print("✅ 后置处理完成")
    else:
        print("❌ 后置处理失败")

# 图片提取功能使用指南

## 概述

本项目新增了图片提取功能，可以从资讯正文、RSS feed或网页中自动提取第一张图片作为科技资讯的配图。

## 功能特性

### 1. 多源图片提取
- **RSS Feed**: 从RSS条目的enclosures、media:content、content、summary等字段提取图片
- **网页内容**: 从HTML页面的meta标签、img标签、背景图片等提取图片
- **Markdown内容**: 从Markdown格式的内容中提取图片链接

### 2. 智能图片识别
- 优先提取Open Graph图片 (`og:image`)
- 其次提取Twitter图片 (`twitter:image`)
- 然后提取页面中的第一张img标签图片
- 最后提取CSS背景图片

### 3. 图片URL验证
- 支持相对路径转绝对路径
- 验证图片URL的有效性
- 支持常见图片格式：jpg、jpeg、png、gif、webp、bmp、svg

## 使用方法

### 1. 基本使用

```python
from utils.image_extractor import extract_first_image_from_content

# 从HTML内容中提取图片
html_content = """
<html>
<head>
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body>
    <img src="https://example.com/first-image.png" alt="第一张图片">
</body>
</html>
"""

image_url = extract_first_image_from_content(html_content, "https://example.com", "html")
print(f"提取的图片URL: {image_url}")
```

### 2. RSS Feed图片提取

```python
from crawler.rss_parser import extract_rss_entry
import feedparser

# 解析RSS feed
feed = feedparser.parse("https://example.com/feed.xml")

for entry in feed.entries:
    result = extract_rss_entry(entry, feed, "https://example.com/feed.xml")
    print(f"标题: {result['title']}")
    print(f"图片: {result.get('image_url', '无图片')}")
```

### 3. 网页爬取时提取图片

```python
from crawler.web_crawler import fetch_webpage_content

# 爬取网页并提取图片
content, html, image_url = fetch_webpage_content("https://example.com/article")
print(f"文章内容: {content[:100]}...")
print(f"图片URL: {image_url}")
```

## 配置说明

### 1. 环境变量

图片提取功能无需额外配置，会自动集成到现有的数据处理流程中。

### 2. 依赖安装

确保安装了必要的依赖：

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `beautifulsoup4`: HTML解析
- `requests`: HTTP请求
- `Pillow`: 图片处理（可选）

## 数据流程

### 1. RSS数据处理流程

```
RSS Feed → extract_rss_entry() → 提取图片URL → 保存到image_url字段
```

### 2. 网页爬取流程

```
网页URL → fetch_webpage_content() → 提取图片URL → 返回图片URL
```

### 3. 新闻处理流程

```
新闻条目 → process_hotspot_with_summary() → 检查图片URL → 更新条目
```

## 输出格式

处理后的新闻条目会包含 `image_url` 字段：

```json
{
    "title": "文章标题",
    "url": "https://example.com/article",
    "content": "文章内容...",
    "image_url": "https://example.com/image.jpg",
    "published": "2024-01-01 12:00:00",
    "source": "来源"
}
```

## 测试

运行图片提取功能测试：

```bash
python tests/test_image_extractor.py
```

测试内容包括：
- 基本图片提取功能
- RSS图片提取
- 真实网站图片提取（可选）

## 常见问题

### 1. 图片提取失败

**问题**: 某些网站的图片无法提取
**解决方案**: 
- 检查网站是否使用了JavaScript动态加载图片
- 确认图片URL是否为相对路径
- 查看日志中的详细错误信息

### 2. 图片URL无效

**问题**: 提取的图片URL无法访问
**解决方案**:
- 使用 `validate_image_url()` 方法验证URL
- 检查图片URL是否需要特殊的User-Agent
- 确认图片服务器是否正常工作

### 3. 性能问题

**问题**: 图片提取影响处理速度
**解决方案**:
- 图片提取是异步进行的，不会阻塞主要内容处理
- 可以设置超时时间控制图片验证
- 对于大量数据，可以考虑缓存图片URL

## 扩展功能

### 1. 自定义图片提取规则

可以扩展 `ImageExtractor` 类，添加特定网站的图片提取规则：

```python
class CustomImageExtractor(ImageExtractor):
    def _extract_from_html(self, html_content: str, base_url: str = "") -> Optional[str]:
        # 添加自定义提取逻辑
        if "example.com" in base_url:
            # 特定网站的提取规则
            pass
        return super()._extract_from_html(html_content, base_url)
```

### 2. 图片下载和存储

可以扩展功能，将图片下载到本地存储：

```python
import requests
from pathlib import Path

def download_image(image_url: str, save_path: str):
    response = requests.get(image_url)
    if response.status_code == 200:
        Path(save_path).write_bytes(response.content)
        return True
    return False
```

## 更新日志

- **v1.0.0**: 初始版本，支持基本的图片提取功能
- **v1.1.0**: 添加RSS feed图片提取
- **v1.2.0**: 集成到新闻处理流程
- **v1.3.0**: 添加图片URL验证功能 
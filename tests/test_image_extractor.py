#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片提取功能测试脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_extractor import ImageExtractor, extract_first_image_from_content
from crawler.rss_parser import extract_rss_entry
import feedparser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_extractor():
    """测试图片提取器"""
    print("=== 测试图片提取器 ===")
    
    extractor = ImageExtractor()
    
    # 测试HTML内容
    html_content = """
    <html>
    <head>
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
    </head>
    <body>
        <img src="https://example.com/first-image.png" alt="第一张图片">
        <img src="https://example.com/second-image.jpg" alt="第二张图片">
        <div style="background-image: url('https://example.com/bg-image.png')"></div>
    </body>
    </html>
    """
    
    image_url = extractor.extract_first_image(html_content, "https://example.com", "html")
    print(f"从HTML提取的图片: {image_url}")
    
    # 测试Markdown内容
    markdown_content = """
    # 测试文章
    
    这是一张图片：
    ![测试图片](https://example.com/markdown-image.jpg)
    
    还有一张HTML图片：
    <img src="https://example.com/html-image.png" alt="HTML图片">
    """
    
    image_url = extractor.extract_first_image(markdown_content, "https://example.com", "markdown")
    print(f"从Markdown提取的图片: {image_url}")

def test_rss_image_extraction():
    """测试RSS图片提取"""
    print("\n=== 测试RSS图片提取 ===")
    
    # 模拟RSS条目
    rss_content = """
    <rss version="2.0">
    <channel>
        <item>
            <title>测试文章标题</title>
            <link>https://example.com/article</link>
            <description>
                <![CDATA[
                <p>这是一篇测试文章</p>
                <img src="https://example.com/rss-image.jpg" alt="RSS图片">
                <p>更多内容...</p>
                ]]>
            </description>
            <enclosure url="https://example.com/enclosure-image.png" type="image/png" length="12345"/>
        </item>
    </channel>
    </rss>
    """
    
    # 解析RSS
    feed = feedparser.parse(rss_content)
    if feed.entries:
        entry = feed.entries[0]
        result = extract_rss_entry(entry, feed, "https://example.com/feed")
        print(f"RSS条目图片: {result.get('image_url', '无图片')}")

def test_real_website():
    """测试真实网站图片提取"""
    print("\n=== 测试真实网站图片提取 ===")
    
    # 这里可以添加一些真实网站的测试
    test_urls = [
        "https://www.36kr.com/p/123456789",
        "https://www.ithome.com/0/123/456.htm",
        "https://juejin.cn/post/123456789"
    ]
    
    for url in test_urls:
        try:
            from crawler.web_crawler import fetch_webpage_content
            content, html, image_url = fetch_webpage_content(url, timeout=10)
            print(f"网站: {url}")
            print(f"图片: {image_url}")
            print("---")
        except Exception as e:
            print(f"测试网站 {url} 失败: {str(e)}")

def main():
    """主测试函数"""
    print("开始测试图片提取功能...")
    
    # 测试基本图片提取
    test_image_extractor()
    
    # 测试RSS图片提取
    test_rss_image_extraction()
    
    # 测试真实网站（可选，需要网络连接）
    # test_real_website()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 
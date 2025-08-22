#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片提取功能示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_extractor import ImageExtractor, extract_first_image_from_content

def main():
    """演示图片提取功能"""
    print("=== 图片提取功能演示 ===\n")
    
    # 创建图片提取器实例
    extractor = ImageExtractor()
    
    # 示例1: 从HTML内容中提取图片
    print("1. 从HTML内容中提取图片:")
    html_content = """
    <html>
    <head>
        <meta property="og:image" content="https://img.36krcdn.com/20240101/v2_1234567890.jpg">
        <meta name="twitter:image" content="https://img.36krcdn.com/20240101/v2_1234567891.jpg">
    </head>
    <body>
        <h1>科技新闻标题</h1>
        <img src="https://img.36krcdn.com/20240101/v2_1234567892.png" alt="第一张图片">
        <p>这是文章内容...</p>
        <img src="https://img.36krcdn.com/20240101/v2_1234567893.jpg" alt="第二张图片">
    </body>
    </html>
    """
    
    image_url = extractor.extract_first_image(html_content, "https://www.36kr.com", "html")
    print(f"   提取的图片URL: {image_url}")
    print()
    
    # 示例2: 从Markdown内容中提取图片
    print("2. 从Markdown内容中提取图片:")
    markdown_content = """
    # AI技术突破
    
    这是一篇关于AI技术突破的文章。
    
    ![AI技术图片](https://img.ithome.com/20240101/ai_breakthrough.jpg)
    
    更多内容...
    
    <img src="https://img.ithome.com/20240101/ai_demo.png" alt="AI演示">
    """
    
    image_url = extractor.extract_first_image(markdown_content, "https://www.ithome.com", "markdown")
    print(f"   提取的图片URL: {image_url}")
    print()
    
    # 示例3: 验证图片URL
    print("3. 验证图片URL:")
    test_urls = [
        "https://img.36krcdn.com/20240101/v2_1234567890.jpg",
        "https://img.ithome.com/20240101/ai_breakthrough.jpg",
        "https://example.com/nonexistent.jpg"
    ]
    
    for url in test_urls:
        is_valid = extractor.validate_image_url(url, timeout=5)
        print(f"   {url}: {'有效' if is_valid else '无效'}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main() 
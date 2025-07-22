#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片提取工具：从HTML内容、RSS feed或网页中提取第一张图片
"""

import re
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from crawler.web_crawler import fetch_webpage_content

# 配置日志
logger = logging.getLogger(__name__)

class ImageExtractor:
    """图片提取器类"""
    
    def __init__(self):
        # 图片文件扩展名
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        # 常见的图片CDN域名
        self.image_cdns = {
            'img.36krcdn.com', 'cdn.36kr.com', 'img.ithome.com', 'img.juejin.cn',
            'img.51cto.com', 'img.csdn.net', 'img.sspai.com', 'img.ifanr.com',
            'img.huxiu.com', 'img.coolapk.com', 'img.v2ex.com', 'img.hostloc.com'
        }
    
    def extract_first_image(self, content: str, base_url: str = "", source_type: str = "html") -> Optional[str]:
        """
        提取第一张图片URL
        
        参数:
            content: 内容（HTML、RSS内容等）
            base_url: 基础URL，用于处理相对路径
            source_type: 内容类型 ("html", "rss", "markdown")
            
        返回:
            第一张图片的URL，如果没有找到则返回None
        """
        if not content:
            return None
            
        try:
            if source_type == "html":
                return self._extract_from_html(content, base_url)
            elif source_type == "rss":
                return self._extract_from_rss(content, base_url)
            elif source_type == "markdown":
                return self._extract_from_markdown(content, base_url)
            else:
                # 默认按HTML处理
                return self._extract_from_html(content, base_url)
        except Exception as e:
            logger.warning(f"提取图片时发生错误: {str(e)}")
            return None
    
    def _extract_from_html(self, html_content: str, base_url: str = "") -> Optional[str]:
        """从HTML内容中提取第一张图片，增强多种策略"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. Open Graph
            og_image = self._extract_og_image(soup)
            if og_image:
                return self._normalize_url(og_image, base_url)

            # 2. Twitter
            twitter_image = self._extract_twitter_image(soup)
            if twitter_image:
                return self._normalize_url(twitter_image, base_url)

            # 3. meta[itemprop=image]
            meta_img = soup.find('meta', attrs={'itemprop': 'image'})
            if meta_img and meta_img.get('content'):
                return self._normalize_url(meta_img['content'], base_url)

            # 4. link[rel=image_src]
            link_img = soup.find('link', rel='image_src')
            if link_img and link_img.get('href'):
                return self._normalize_url(link_img['href'], base_url)

            # 5. figure/picture
            for fig in soup.find_all(['figure', 'picture']):
                img = fig.find('img')
                if img:
                    img_url = self._extract_img_url(img)
                    if img_url and self._is_valid_image_url(img_url):
                        return self._normalize_url(img_url, base_url)

            # 6. img标签
            img_tags = soup.find_all('img')
            for img in img_tags:
                img_url = self._extract_img_url(img)
                if img_url and self._is_valid_image_url(img_url):
                    normalized_url = self._normalize_url(img_url, base_url)
                    if normalized_url and self.is_reasonable_image_size(normalized_url):
                        return normalized_url

            # 7. background-image
            bg_image = self._extract_background_image(soup)
            if bg_image:
                return self._normalize_url(bg_image, base_url)

        except Exception as e:
            logger.warning(f"从HTML提取图片时发生错误: {str(e)}")
        return None
    
    def _extract_from_rss(self, rss_content: str, base_url: str = "") -> Optional[str]:
        """从RSS内容中提取第一张图片"""
        try:
            # RSS内容通常是HTML格式的，按HTML处理
            return self._extract_from_html(rss_content, base_url)
        except Exception as e:
            logger.warning(f"从RSS提取图片时发生错误: {str(e)}")
            return None
    
    def _extract_from_markdown(self, markdown_content: str, base_url: str = "") -> Optional[str]:
        """从Markdown内容中提取第一张图片，增强HTML兜底"""
        try:
            # Markdown图片
            img_pattern = r'!\[.*?\]\(([^)]+)\)'
            matches = re.findall(img_pattern, markdown_content)
            for match in matches:
                if self._is_valid_image_url(match):
                    normalized_url = self._normalize_url(match, base_url)
                    if normalized_url and self.is_reasonable_image_size(normalized_url):
                        return normalized_url
            # HTML img
            html_img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
            html_matches = re.findall(html_img_pattern, markdown_content)
            for match in html_matches:
                if self._is_valid_image_url(match):
                    normalized_url = self._normalize_url(match, base_url)
                    if normalized_url and self.is_reasonable_image_size(normalized_url):
                        return normalized_url
            # 兜底：直接用HTML解析
            html_img = self._extract_from_html(markdown_content, base_url)
            if html_img:
                return html_img
        except Exception as e:
            logger.warning(f"从Markdown提取图片时发生错误: {str(e)}")
        return None
    
    def _extract_og_image(self, soup: BeautifulSoup) -> Optional[str]:
        """提取Open Graph图片"""
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # 尝试其他常见的og:image变体
        for attr in ['property', 'name']:
            for value in ['og:image', 'og:image:url', 'og:image:secure_url']:
                meta = soup.find('meta', attrs={attr: value})
                if meta and meta.get('content'):
                    return meta['content']
        
        return None
    
    def _extract_twitter_image(self, soup: BeautifulSoup) -> Optional[str]:
        """提取Twitter图片"""
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # 尝试其他Twitter图片变体
        for value in ['twitter:image:src', 'twitter:image0']:
            meta = soup.find('meta', attrs={'name': value})
            if meta and meta.get('content'):
                return meta['content']
        
        return None
    
    def _extract_img_url(self, img_tag) -> Optional[str]:
        """从img标签中提取图片URL，支持更多属性"""
        # 优先级顺序
        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-original-src', 'srcset', 'data-srcset']:
            val = img_tag.get(attr)
            if val:
                # srcset 取第一个
                if attr.endswith('srcset') and ',' in val:
                    val = val.split(',')[0].split()[0]
                return val
        return None
    
    def _extract_background_image(self, soup: BeautifulSoup) -> Optional[str]:
        """从CSS背景图片中提取"""
        # 查找包含background-image的元素
        elements_with_bg = soup.find_all(style=True)
        for element in elements_with_bg:
            style = element.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', style)
            if bg_match:
                return bg_match.group(1)
        
        return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否为有效的图片URL，增强对主流站点的支持，并丢弃icon类图片"""
        if not url:
            return False
        if url.startswith('data:image/'):
            return True
        parsed = urlparse(url)
        path = parsed.path.lower()
        # 丢弃icon类图片
        icon_keywords = ['icon', 'favicon', 'logo', 'avatar', 'profile', 'sprite']
        if any(kw in path for kw in icon_keywords):
            return False
        # 丢弃常见极小尺寸图片（如16x16, 32x32等）
        size_pattern = r'([_/\-]|^)(1[6-9]|2[0-9]|3[0-2])x(1[6-9]|2[0-9]|3[0-2])([_/\.-]|$)'
        if re.search(size_pattern, path):
            return False
        if any(path.endswith(ext) for ext in self.image_extensions):
            return True
        domain = parsed.netloc.lower()
        if any(site in domain for site in ['juejin.cn', 'csdn.net', 'zhihu.com', '36kr.com', 'ithome.com', 'huxiu.com']):
            return True
        img_paths = ['/img/', '/image/', '/images/', '/pic/', '/picture/', '/photo/']
        if any(img_path in path for img_path in img_paths):
            return True
        return False
    
    def _normalize_url(self, url: str, base_url: str = "") -> Optional[str]:
        """标准化图片URL"""
        if not url:
            return None
        
        # 处理数据URL
        if url.startswith('data:image/'):
            return url
        
        # 处理相对路径
        if not url.startswith(('http://', 'https://')):
            if base_url:
                return urljoin(base_url, url)
            else:
                return None
        
        return url
    
    def extract_images_from_feed_entry(self, entry: Dict[str, Any], base_url: str = "") -> Optional[str]:
        """
        从RSS feed条目中提取图片，增强对media:thumbnail、itunes:image等支持
        """
        # 1. enclosures
        if 'enclosures' in entry and entry['enclosures']:
            for enclosure in entry['enclosures']:
                if isinstance(enclosure, dict) and enclosure.get('type', '').startswith('image/'):
                    return self._normalize_url(enclosure.get('href', ''), base_url)
        # 2. media_content
        if 'media_content' in entry and entry['media_content']:
            for media in entry['media_content']:
                if isinstance(media, dict) and media.get('type', '').startswith('image/'):
                    return self._normalize_url(media.get('url', ''), base_url)
        # 3. media_thumbnail
        if 'media_thumbnail' in entry and entry['media_thumbnail']:
            for thumb in entry['media_thumbnail']:
                if isinstance(thumb, dict) and thumb.get('url'):
                    return self._normalize_url(thumb['url'], base_url)
        # 4. itunes:image
        if 'itunes_image' in entry and entry['itunes_image']:
            return self._normalize_url(entry['itunes_image'], base_url)
        # 5. content
        if 'content' in entry and entry['content']:
            return self.extract_first_image(entry['content'], base_url, "html")
        # 6. summary
        if 'summary' in entry and entry['summary']:
            return self.extract_first_image(entry['summary'], base_url, "html")
        return None
    
    def validate_image_url(self, url: str, timeout: int = 5) -> bool:
        """
        验证图片URL是否可访问
        
        参数:
            url: 图片URL
            timeout: 超时时间（秒）
            
        返回:
            是否可访问
        """
        if not url or url.startswith('data:image/'):
            return True
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            return content_type.startswith('image/')
        except Exception as e:
            logger.debug(f"验证图片URL失败: {url}, 错误: {str(e)}")
            return False

    def is_reasonable_image_size(self, url, min_width=600, min_height=400, min_filesize=20*1024, min_ratio=0.5, max_ratio=2.0, timeout=5):
        """检测图片尺寸和文件大小是否合理，宽>=600，高>=400，长宽比0.5~2.0，文件大小>=20KB，且不是二维码"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            resp = requests.get(url, timeout=timeout, stream=True)
            resp.raise_for_status()
            content = resp.content
            # 文件大小判断
            if len(content) < min_filesize:
                logger.debug(f'图片文件过小: {url}, {len(content)} bytes')
                return False
            img = Image.open(BytesIO(content))
            width, height = img.size
            if width < min_width or height < min_height:
                logger.debug(f'图片尺寸过小: {url}, {width}x{height}')
                return False
            ratio = width / height if height > 0 else 0
            if not (min_ratio <= ratio <= max_ratio):
                logger.debug(f'图片长宽比不合规: {url}, ratio={ratio:.2f}')
                return False
            # 检测是否为二维码
            try:
                from pyzbar.pyzbar import decode as zbar_decode
                qr_results = zbar_decode(img)
                if qr_results:
                    logger.debug(f'检测到二维码图片: {url}')
                    return False
            except Exception as e:
                logger.debug(f'二维码检测失败(可忽略): {e}')
            return True
        except Exception as e:
            logger.debug(f'检测图片尺寸失败: {url}, 错误: {e}')
            return False

# 创建全局实例
image_extractor = ImageExtractor()

def extract_first_image_from_content(content: str, base_url: str = "", source_type: str = "html") -> Optional[str]:
    """
    从内容中提取第一张图片的便捷函数
    
    参数:
        content: 内容
        base_url: 基础URL
        source_type: 内容类型
        
    返回:
        第一张图片的URL
    """
    return image_extractor.extract_first_image(content, base_url, source_type)

def extract_image_from_feed_entry(entry: Dict[str, Any], base_url: str = "") -> Optional[str]:
    """
    从RSS feed条目中提取图片的便捷函数
    
    参数:
        entry: RSS条目字典
        base_url: 基础URL
        
    返回:
        第一张图片的URL
    """
    return image_extractor.extract_images_from_feed_entry(entry, base_url) 

def assign_image_url_to_items(items, default_image_url=""):
    """
    批量为每条 item 自动补充 image_url 字段。
    优先 content、desc、summary，最后抓取网页HTML。
    针对主流站点和desc/summary为HTML的情况增强。
    兜底网页抓取统一用 web_crawler 能力。
    带详细日志。
    """
    import requests
    for idx, item in enumerate(items):
        content = item.get('content') or ''
        desc = item.get('desc') or ''
        summary = item.get('summary') or ''
        url = item.get('url') or ''
        logger.debug(f"[配图调试] 第{idx+1}条 {item.get('title','')[:20]}... content[:100]={content[:100]!r} desc[:100]={desc[:100]!r} summary[:100]={summary[:100]!r} url={url}")
        img_url = extract_first_image_from_content(content, base_url=url, source_type="html")
        if img_url:
            logger.info(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... 从content提取到图片: {img_url}")
        # desc/summary优先用HTML解析
        if not img_url:
            img_url = extract_first_image_from_content(desc, base_url=url, source_type="html")
            if img_url:
                logger.info(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... 从desc(HTML)提取到图片: {img_url}")
        if not img_url:
            img_url = extract_first_image_from_content(summary, base_url=url, source_type="html")
            if img_url:
                logger.info(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... 从summary(HTML)提取到图片: {img_url}")
        # 统一兜底：用 web_crawler 能力抓取网页HTML
        if not img_url and url:
            try:
                logger.info(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... 用web_crawler抓取网页HTML提取图片: {url}")
                _, html, _ = fetch_webpage_content(url, fetch_html_only=True, max_retries=1)
                if html:
                    img_url = extract_first_image_from_content(html, base_url=url, source_type="html")
                    if img_url:
                        logger.info(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... web_crawler网页HTML抓取到图片: {img_url}")
                    else:
                        logger.warning(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... web_crawler网页HTML未提取到图片")
                else:
                    logger.warning(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... web_crawler未能获取HTML")
            except Exception as e:
                logger.warning(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... web_crawler网页HTML抓取异常: {e}")
        if not img_url:
            logger.warning(f"[配图] 第{idx+1}条 {item.get('title','')[:20]}... 未提取到图片，url: {url}")
        item['image_url'] = img_url if img_url else default_image_url 
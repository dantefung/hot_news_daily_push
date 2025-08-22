import os
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.image_extractor import assign_image_url_to_items

def test_hotspots_image_extraction():
    jsonl_path = os.path.join('test_data', 'hotspots_2025-07-22_14-58-57.jsonl')
    if not os.path.exists(jsonl_path):
        print(f"文件不存在: {jsonl_path}")
        return
    items = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    print(f"共加载 {len(items)} 条新闻")
    assign_image_url_to_items(items)
    success = 0
    for idx, item in enumerate(items):
        title = item.get('title', '')
        url = item.get('url', '')
        image_url = item.get('image_url', '')
        print(f"[{idx+1:03d}] 标题: {title[:40]}\n     URL: {url}\n     提取图片: {image_url if image_url else '❌未提取到'}\n")
        if image_url:
            success += 1
    print(f"\n提取成功 {success}/{len(items)}，成功率: {success/len(items)*100:.2f}%")

if __name__ == "__main__":
    test_hotspots_image_extraction() 
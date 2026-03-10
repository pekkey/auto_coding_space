#!/usr/bin/env python3
"""
天下要闻 - ClawHub 热门技能集成
"""
import json, pathlib, subprocess, logging, sys
from datetime import datetime, timezone

log = logging.getLogger('morning-brief')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s', datefmt='%H:%M:%S')

DATA = pathlib.Path('/home/admin/edict/data')

def fetch_clawhub_trending(max_items=10):
    """从 ClawHub 获取热门技能（简化版）"""
    try:
        result = subprocess.run(
            ['clawhub', 'explore', '--limit', str(max_items), '--sort', 'rating'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        if result.returncode != 0:
            log.warning(f'ClawHub 查询失败: {result.stderr.decode()}')
            return []
        
        # 解析纯文本输出
        output = result.stdout.decode('utf-8', errors='ignore')
        items = []
        
        for line in output.split('\n')[:max_items]:
            line = line.strip()
            if not line or line.startswith('-') or line.startswith('Fetching'):
                continue
            
            # 提取 slug（第一个单词）
            parts = line.split()
            if not parts:
                continue
            
            slug = parts[0]
            display_name = slug.replace('-', ' ').title()
            
            items.append({
                'title': display_name,
                'summary': 'ClawHub 热门技能',
                'link': f'https://clawhub.ai/skills/{slug}',
                'pub_date': '',
                'image': '',
                'source': 'ClawHub'
            })
        
        log.info(f'ClawHub: 成功解析 {len(items)} 个技能')
        return items
        
    except Exception as e:
        log.error(f'ClawHub 采集异常: {e}')
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    
    # 获取 ClawHub 技能
    clawhub_items = fetch_clawhub_trending(args.limit)
    
    # 读取现有的天下要闻数据
    morning_brief_file = DATA / 'morning_brief.json'
    if morning_brief_file.exists():
        with open(morning_brief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'date': datetime.now().strftime('%Y%m%d'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'categories': {}
        }
    
    # 添加 ClawHub 分类
    data['categories']['ClawHub'] = clawhub_items
    
    # 保存
    with open(morning_brief_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    total = sum(len(v) for v in data['categories'].values())
    log.info(f'✅ 完成：共 {total} 条要闻（含 {len(clawhub_items)} 个 ClawHub 技能）')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
天下要闻 - ClawHub 热门技能集成
"""
import json, pathlib, subprocess, logging

log = logging.getLogger('morning_brief')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s', datefmt='%H:%M:%S')

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data'

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
            if not slug:
                continue
            
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
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    
    # 获取 ClawHub 技能
    clawhub_items = fetch_clawhub_trending(args.limit)
    
    # 保存
    if args.output:
        output_file = pathlib.Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'ClawHub': clawhub_items}, 'generated_at': 'now'}, f, indent=2, ensure_ascii=False)
        
        log.info(f'✅ 完成：{len(clawhub_items)} 个技能 → {output_file}')
    else:
        # 输出到控制台
        print(json.dumps({'ClawHub': clawhub_items}, 'generated_at': 'now'}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

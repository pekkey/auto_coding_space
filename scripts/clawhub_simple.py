#!/usr/bin/env python3
"""
ClawHub 热门技能采集脚本 - 简化版
直接解析 clawhub explore 命令的纯文本输出
"""
import subprocess, json, pathlib, logging

log = logging.getLogger('clawhub_simple')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s', datefmt='%H:%M:%S')

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data'

def fetch_clawhub_trending(max_items=10):
    """从 ClawHub 获取热门技能（简化解析）"""
    try:
        # 使用 clawhub CLI 获取热门技能（纯文本输出，不带 --json）
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
        
        # 按行分割，每行一个技能
        for line in output.split('\n'):
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
            
            # 转换显示名称
            display_name = slug.replace('-', ' ').title()
            
            # 添加到结果列表
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
    parser.add_argument('--limit', type=int, default=10, help='获取技能数量')
    args = parser.parse_args()
    
    # 获取 ClawHub 技能
    clawhub_items = fetch_clawhub_trending(args.limit)
    
    # 构造结果
    result = {
        'ClawHub': clawhub_items
    }
    
    # 保存到文件
    output_file = DATA / 'clawhub_simple.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    log.info(f'✅ 完成：{len(clawhub_items)} 个技能 → {output_file.name}')

if __name__ == '__main__':
    main()

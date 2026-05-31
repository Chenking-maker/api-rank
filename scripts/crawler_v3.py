#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中转站智能爬虫 v9.0 - 精简版
核心功能：
1. 检查已收录站点是否失效
2. 检查失效站点是否恢复
3. 搜索发现新站点（Bing文章爬取 + GitHub README + DuckDuckGo补充）
"""
import re
import json
import time
import random
import os
import sys
from urllib.parse import urlparse, quote
from datetime import datetime
from typing import List, Dict, Set, Tuple

import requests
from bs4 import BeautifulSoup

HAS_SCRAPLING = False
try:
    from scrapling.fetchers import StealthyFetcher
    HAS_SCRAPLING = True
    print("[OK] Scrapling 可用（仅用于绕过Cloudflare）")
except:
    print("[INFO] Scrapling 不可用，全部用 requests")

# ============ 配置 ============

EXCLUDE_DOMAINS = [
    # 搜索引擎/社交平台
    'github.com', 'google.com', 'googleapis.com', 'google.co',
    'baidu.com', 'bilibili.com', 'douyin.com', 'iesdouyin.com',
    'xiaohongshu.com', 'zhihu.com', 'weibo.com', 'qq.com',
    'wechat.com', 'weixin.qq.com', 'facebook.com', 'instagram.com',
    'twitter.com', 'x.com', 'linkedin.com', 'pinterest.com',
    'youtube.com', 'tiktok.com', 'telegram.org', 'discord.com',
    # 云服务/CDN
    'aliyun.com', 'tencent.com', 'myqcloud.com', 'alicdn.com',
    'bdstatic.com', 'cloudflare.com', 'workers.dev', 'vercel.app',
    'netlify.app', 'github.io', 'herokuapp.com', 'railway.app',
    # 开发者社区/文档
    'csdn.net', 'juejin.cn', 'segmentfault.com', 'cnblogs.com',
    'stackoverflow.com', 'reddit.com', 'dev.to', 'medium.com',
    'duckduckgo.com', 'bing.com', 'search.yahoo.com',
    'pypi.org', 'npmjs.com', 'crates.io', 'tieba.baidu.com',
    'mozilla.org', 'w3.org', 'wikipedia.org', 'microsoft.com',
    'apple.com', 'amazon.com', 'aws.amazon.com', 'nginx.org',
    'apache.org', 'python.org', 'nodejs.org', 'docker.com',
    # 官方AI平台（不是中转站）
    'openai.com', 'anthropic.com', 'deepseek.com', 'gemini.google.com',
    'platform.openai.com', 'console.anthropic.com',
    'kimi.com', 'moonshot.cn', 'platform.kimi.com',
    'yiyan.baidu.com', 'tongyi.aliyun.com', 'qianwen.aliyun.com',
    'chatglm.cn', 'bigmodel.cn', 'zhipuai.cn',
    'claude.ai', 'chatgpt.com', 'chat.openai.com',
    'huggingface.co', 'poe.com', 'pika.art',
    # 云服务商/文档站
    'oracle.com', 'cloud.tencent.com', 'apifox.com',
    'huaweicloud.com', 'volcengine.com', 'bytedance.com',
    'docs.', 'documentation.', 'support.',
    # 非中转站（误判过滤）
    'douban.com', 'doubao.com', 'doubao.cn', 'toutiao.com',
    'britannica.com', 'history.com', 'wikiwand.com',
    '360.cn', 'baoku.360.cn', 'sj.qq.com',
    'aitop100.cn', 'aigc.cn',
    # 政府机构/教育/新闻
    '.gov.', '.edu.', '.mil.', '.org.',
    'news.', 'blog.', 'wiki.',
    # 示例/备案
    'beian.cac.gov.cn', 'beian.miit.gov.cn', 'miit.gov.cn',
    'example.com', 'example.org', 'example.net', 'test.com',
]

STATIC_EXTENSIONS = {
    '.css', '.js', '.map', '.json', '.xml', '.svg', '.woff', '.woff2',
    '.ttf', '.eot', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.mp4', '.mp3', '.pdf', '.zip', '.tar', '.gz', '.rar', '.avi', '.mov',
}

STATION_KEYWORDS = [
    'api', 'ai', 'gpt', 'claude', 'openai', 'forward', 'proxy',
    '中转', '代理', '转发', '模型', '接口', 'key', 'llm',
    'chatgpt', 'gemini', 'deepseek', 'kimi', '通义', '文心',
    'reseller', 'relay', 'gateway', 'reverse', 'alternative',
]

DATA_DIR = 'data'
PENDING_FILE = f'{DATA_DIR}/pending_stations.json'
DEAD_FILE = f'{DATA_DIR}/dead_sites.json'
REPORT_FILE = f'{DATA_DIR}/crawler_report.json'
CACHE_FILE = f'{DATA_DIR}/daily_check_cache.json'

# 每日新站点上限（达到后停止搜索）
MAX_NEW_SITES_PER_DAY = 10

# 搜索时跳过的域名（非内容页面）
SKIP_SEARCH_DOMAINS = {
    'github.com', 'google.com', 'youtube.com', 'facebook.com',
    'instagram.com', 'twitter.com', 'x.com', 'tiktok.com',
    'pinterest.com', 'linkedin.com', 'douyin.com',
    'bilibili.com', 'weibo.com', 'qq.com', 'baidu.com',
}


# ============ 工具函数 ============

def get_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain
    except:
        return ''


def is_static_resource(url: str) -> bool:
    try:
        path = urlparse(url).path.lower()
        return any(path.endswith(ext) for ext in STATIC_EXTENSIONS)
    except:
        return False


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith('http'):
        url = f'https://{url}'
    return url.rstrip('/')


# ============ 爬虫主类 ============

class SmartCrawler:
    """API中转站爬虫 v9.0"""

    def __init__(self):
        self.existing_domains: Set[str] = set()
        self.existing_stations: List[Dict] = []
        self.pending_domains: Set[str] = set()
        self.dead_domains: Set[str] = set()
        self.pending_stations: List[Dict] = []
        self.dead_sites: List[Dict] = []
        self.new_discovered: List[Dict] = []
        self.new_recovered: List[Dict] = []
        self.recovered_sites: List[Dict] = []
        self.new_dead: List[Dict] = []
        self.session = None
        self.start_time = 0
        self.check_cache: Dict[str, Dict] = {}

    def init(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        })

    # ---- 数据加载/保存 ----

    def load_all_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load_existing_from_index()
        try:
            with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                self.pending_stations = json.load(f)
                self.pending_stations = [s for s in self.pending_stations
                                         if s.get('status') not in ('approved', 'rejected')]
                self.pending_domains = {get_domain(s.get('url', '')) for s in self.pending_stations}
                print(f"  已加载 {len(self.pending_stations)} 个待审核站点")
        except:
            self.pending_stations = []
        try:
            with open(DEAD_FILE, 'r', encoding='utf-8') as f:
                self.dead_sites = json.load(f)
                self.dead_sites = [s for s in self.dead_sites if s.get('status') != 'recovered']
                self.dead_domains = {get_domain(s.get('url', '')) for s in self.dead_sites}
                print(f"  已加载 {len(self.dead_sites)} 个失效站点")
        except:
            self.dead_sites = []
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                self.check_cache = json.load(f)
            today = datetime.now().strftime('%Y-%m-%d')
            self.check_cache = {k: v for k, v in self.check_cache.items() if v.get('date') == today}
            print(f"  已加载 {len(self.check_cache)} 条今日检测缓存")
        except:
            self.check_cache = {}

    def _load_existing_from_index(self):
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            cards = soup.select('.rank-card')
            for card in cards:
                name_tag = card.select_one('.rank-name')
                name = name_tag.get_text(strip=True) if name_tag else ''
                url_match = re.search(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', str(card))
                if url_match:
                    href = url_match.group(0)
                    domain = url_match.group(1).lower().replace('www.', '')
                    if domain and len(domain) > 3:
                        self.existing_domains.add(domain)
                        self.existing_stations.append({'url': normalize_url(href), 'name': name, 'domain': domain})
            print(f"  从index.html提取 {len(self.existing_domains)} 个域名（{len(cards)} 个rank-card）")
        except Exception as e:
            print(f"  [WARN] 无法读取index.html: {e}")

    def save_all_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.pending_stations, f, ensure_ascii=False, indent=2)
        with open(DEAD_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.dead_sites, f, ensure_ascii=False, indent=2)
        site_status = {
            'updated_at': datetime.now().isoformat(),
            'recovered': self.recovered_sites,
            'new_dead': [{'url': s.get('url', ''), 'name': s.get('name', ''),
                         'domain': s.get('domain', ''), 'reason': s.get('reason', '')} for s in self.new_dead],
        }
        with open(f'{DATA_DIR}/site_status.json', 'w', encoding='utf-8') as f:
            json.dump(site_status, f, ensure_ascii=False, indent=2)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.check_cache, f, ensure_ascii=False, indent=2)
        self._generate_dead_sites_html()

    def _generate_dead_sites_html(self):
        all_dead = []
        seen_names = set()
        hardcoded_dead = [
            ('非线智能Api', '404错误'), ('PoloAPI', '连接超时'), ('速创API', '无法访问'),
            ('Anyrouter', '无法访问'), ('B4U API', '403禁止'), ('91Code API', '无法访问'),
            ('JAY中转API', '无法访问'), ('超凡API中转站', '无法访问'),
            ('词元无忧API (Token5u)', '无法访问'), ('B.AI (波场)', '无法访问'),
            ('莹的API', 'SSL错误'), ('CloseAI', '无法访问'),
        ]
        recovered_names = {s.get('name', '') for s in self.new_recovered}
        for name, reason in hardcoded_dead:
            is_recovered = any(rname and (rname in name or name in rname) for rname in recovered_names)
            if not is_recovered:
                all_dead.append((name, reason))
                seen_names.add(name)
        for site in self.dead_sites:
            if site.get('status') == 'recovered':
                continue
            name = site.get('name', site.get('domain', ''))
            if name not in seen_names:
                all_dead.append((name, site.get('reason', '无法访问')))
                seen_names.add(name)
        html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>已失效站点 - API排行榜</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d0d14;color:#e0e0e0;min-height:100vh;padding:40px 20px}}
.container{{max-width:800px;margin:0 auto}}h1{{font-size:24px;margin-bottom:8px;color:#ff6b6b}}.subtitle{{color:#888;margin-bottom:24px;font-size:14px}}
.dead-list{{list-style:none}}.dead-list li{{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;background:rgba(255,255,255,.03);border-radius:10px;margin-bottom:8px;border:1px solid rgba(255,107,107,.1)}}
.dead-list li .name{{font-size:15px;font-weight:500}}.dead-list li .reason{{font-size:12px;color:#ff6b6b;background:rgba(255,107,107,.1);padding:2px 10px;border-radius:6px}}
.back{{display:inline-block;margin-top:24px;color:#4ecdc4;text-decoration:none;font-size:14px}}.back:hover{{text-decoration:underline}}.count{{font-size:13px;color:#888;margin-bottom:16px}}
</style></head><body><div class="container">
<h1>⚠️ 已失效站点</h1><p class="subtitle">以下站点无法访问或已停止服务，已自动排到排行榜末尾</p>
<p class="count">共 {len(all_dead)} 个失效站点</p><ul class="dead-list">\n'''
        for name, reason in all_dead:
            html += f'    <li><span class="name">{name}</span><span class="reason">{reason}</span></li>\n'
        html += '</ul>\n<a href="index.html" class="back">← 返回排行榜</a>\n</div></body></html>'
        with open('dead-sites.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  已生成 dead-sites.html（{len(all_dead)} 个失效站点）")

    # ---- 网络请求 ----

    def is_valid_station(self, url: str) -> bool:
        if not url or is_static_resource(url):
            return False
        if not url.startswith('http://') and not url.startswith('https://'):
            return False
        domain = get_domain(url)
        if not domain or len(domain) < 4:
            return False
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
            return False
        for exclude in EXCLUDE_DOMAINS:
            if exclude in domain:
                return False
        if domain in self.existing_domains or domain in self.pending_domains or domain in self.dead_domains:
            return False
        # 子域名去重：api.example.com 和 example.com 视为同一站点
        for existing in self.existing_domains:
            e_parts = existing.split('.')
            d_parts = domain.split('.')
            if len(e_parts) >= 2 and len(d_parts) >= 2:
                e_root = '.'.join(e_parts[-2:]) if len(e_parts) > 2 else existing
                d_root = '.'.join(d_parts[-2:]) if len(d_parts) > 2 else domain
                if e_root == d_root:
                    return False
        combined = f"{domain} {urlparse(url).path.lower()}"
        return any(kw.lower() in combined for kw in STATION_KEYWORDS)

    def http_get(self, url: str, timeout: int = 10) -> Tuple[bool, str]:
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            return (True, resp.text) if resp.status_code == 200 else (False, f"HTTP {resp.status_code}")
        except Exception as e:
            return False, str(e)[:60]

    def stealth_get(self, url: str, timeout: int = 15) -> Tuple[bool, str]:
        if not HAS_SCRAPLING:
            return False, "Scrapling不可用"
        try:
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True, timeout=timeout * 1000)
            return True, str(page.html) if hasattr(page, 'html') else str(page)
        except Exception as e:
            return False, str(e)[:60]

    def check_site_alive(self, url: str) -> Tuple[bool, str]:
        """三级检测：HEAD → GET → Scrapling，带每日缓存（仅缓存存活）"""
        url = normalize_url(url)
        domain = get_domain(url)
        today = datetime.now().strftime('%Y-%m-%d')
        if domain and domain in self.check_cache:
            cached = self.check_cache[domain]
            if cached.get('date') == today and cached.get('alive'):
                return True, cached.get('msg', '今日已检测: 正常')
        # 第1级: HEAD
        try:
            resp = self.session.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                self.check_cache[domain] = {'alive': True, 'date': today, 'msg': f"HTTP {resp.status_code}"}
                return True, f"HTTP {resp.status_code}"
        except:
            pass
        # 第2级: GET
        ok, result = self.http_get(url, timeout=8)
        if ok:
            try:
                soup = BeautifulSoup(result, 'html.parser')
                msg = soup.title.string.strip()[:50] if soup.title else "可访问"
            except:
                msg = "可访问"
            self.check_cache[domain] = {'alive': True, 'date': today, 'msg': msg}
            return True, msg
        # 第3级: Scrapling
        ok, result = self.stealth_get(url, timeout=10)
        if ok:
            self.check_cache[domain] = {'alive': True, 'date': today, 'msg': 'StealthyFetcher可访问'}
            return True, 'StealthyFetcher可访问'
        self.check_cache[domain] = {'alive': False, 'date': today, 'msg': result}
        return False, result

    # ---- 站点检测 ----

    def check_existing_sites(self):
        if not self.existing_stations:
            print("  没有已收录站点URL，跳过失效检测")
            return
        print(f"\n{'='*50}\n检查 {len(self.existing_stations)} 个已收录站点是否失效...\n{'='*50}")
        alive_count = dead_count = 0
        for i, station in enumerate(self.existing_stations):
            url, name, domain = station.get('url', ''), station.get('name', ''), station.get('domain', '')
            if not url:
                continue
            is_alive, msg = self.check_site_alive(url)
            if is_alive:
                alive_count += 1
                print(f"  [{i+1}/{len(self.existing_stations)}] ✓ {name[:20]:20s} 正常")
            else:
                dead_count += 1
                dead_info = {'url': url, 'name': name, 'domain': domain,
                            'died_at': datetime.now().isoformat(), 'reason': msg, 'status': 'dead'}
                self.dead_sites.append(dead_info)
                self.dead_domains.add(domain)
                self.new_dead.append(dead_info)
                print(f"  [{i+1}/{len(self.existing_stations)}] ✗ {name[:20]:20s} 失效! ({msg})")
            time.sleep(0.3)
        print(f"\n  检测完成: {alive_count} 正常, {dead_count} 失效")

        # 自动更新 index.html 中的失效站点标记
        self._update_html_dead_sites()

    def _update_html_dead_sites(self):
        """将失效站点在 index.html 中标记为失效状态"""
        import re, os
        dead_path = os.path.join(DATA_DIR, 'dead_sites.json')
        html_path = os.path.join('.', 'index.html')
        
        if not os.path.exists(dead_path) or not os.path.exists(html_path):
            return
        
        try:
            with open(dead_path, 'r', encoding='utf-8') as f:
                dead_sites = json.load(f)
            
            if not isinstance(dead_sites, list) or len(dead_sites) == 0:
                return
            
            dead_domains = set()
            for site in dead_sites:
                url = site.get('url', '')
                domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].lower()
                if domain:
                    dead_domains.add(domain)
            
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            for domain in dead_domains:
                # 在 rank-card 中查找包含该域名的卡片，添加 dead 标记
                pattern = rf'(class="rank-card[^"]*"[^>]*>.*?href="https?://[^"]*{re.escape(domain)}[^"]*")'
                matches = list(re.finditer(pattern, content, re.DOTALL))
                for match in matches:
                    card_html = match.group(1)
                    if 'data-dead="true"' not in card_html:
                        # 在 class 中添加 dead 标记
                        new_card = card_html.replace('class="rank-card', 'data-dead="true" class="rank-card')
                        content = content.replace(card_html, new_card)
                        modified = True
            
            if modified:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[失效标记] 已在 index.html 中标记 {len(dead_domains)} 个失效站点")
        except Exception as e:
            print(f"[失效标记] 更新失败: {e}")

    def check_dead_recovery(self):
        """检查失效站点是否恢复"""
        # 已知失效站点的URL映射（硬编码，避免每次都搜索）
        KNOWN_DEAD_URLS = {
            '非线智能api': 'https://feixian-api.com',
            'poloapi': 'https://poloapi.com',
            '速创api': 'https://suchuangapi.com',
            'anyrouter': 'https://api.anyrouter.com',
            'b4u api': 'https://b4uapi.com',
            '91code api': 'https://91codeapi.com',
            'jay中转api': 'https://jayapi.com',
            '超凡api中转站': 'https://chaofanapi.com',
            '词元无忧api': 'https://token5u.com',
            'token5u': 'https://token5u.com',
            'b.ai': 'https://b.ai',
            '波场': 'https://b.ai',
            '莹的api': 'https://yingapi.com',
            'closeai': 'https://closeai-asia.com',
        }

        all_dead_to_check = []
        # 1. 从 dead-sites.html 读取
        try:
            with open('dead-sites.html', 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for li in soup.select('.dead-list li'):
                name_tag = li.select_one('.name')
                name = name_tag.get_text(strip=True) if name_tag else ''
                all_dead_to_check.append({'url': '', 'name': name, 'domain': '', 'status': 'dead'})
            print(f"  从dead-sites.html读取 {len(soup.select('.dead-list li'))} 个失效站点")
        except Exception as e:
            print(f"  [WARN] 读取dead-sites.html失败: {e}")
        # 2. 从硬编码映射表匹配URL
        matched_known = 0
        for dead in all_dead_to_check:
            if dead.get('url'):
                continue
            name_lower = dead['name'].lower()
            for key, url in KNOWN_DEAD_URLS.items():
                if key in name_lower or name_lower in key:
                    dead['url'] = url
                    dead['domain'] = get_domain(url)
                    matched_known += 1
                    break
        if matched_known:
            print(f"  从已知URL映射匹配到 {matched_known} 个")
        # 3. 从 index.html 匹配URL
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            db_matches = re.findall(r"name:\s*['\"]([^'\"]+)['\"].*?url:\s*['\"]([^'\"]+)['\"]", html_content)
            for db_name, db_url in db_matches:
                for dead in all_dead_to_check:
                    if not dead['url'] and dead['name']:
                        dname = dead['name'].lower()
                        if db_name.lower() in dname or dname in db_name.lower():
                            dead['url'] = normalize_url(db_url)
                            dead['domain'] = get_domain(db_url)
                            break
            matched = sum(1 for d in all_dead_to_check if d['url'])
            print(f"  从index.html匹配到 {matched} 个URL")
        except:
            pass
        # 4. 爬虫之前检测到的失效站点
        for site in self.dead_sites:
            if site.get('url') and not any(s.get('url') == site['url'] for s in all_dead_to_check):
                all_dead_to_check.append(site)
        # 5. 仍然没有URL的，用搜索引擎查找（兜底）
        no_url = [s for s in all_dead_to_check if not s.get('url')]
        if no_url:
            print(f"\n  {len(no_url)} 个失效站点缺少URL，通过搜索引擎查找...")
            for site in no_url:
                name = site.get('name', '')
                if not name:
                    continue
                found = self._search_url_for_name(f'"{name}" API 中转站', name)
                if found:
                    site['url'] = found
                    site['domain'] = get_domain(found)
                    print(f"    找到: {name} → {found}")
                else:
                    print(f"    未找到: {name}（跳过）")
                time.sleep(1)
        all_dead_to_check = [s for s in all_dead_to_check if s.get('url')]
        if not all_dead_to_check:
            return
        print(f"\n检查 {len(all_dead_to_check)} 个失效站点是否恢复...")
        still_dead = []
        self.recovered_sites = []
        for site in all_dead_to_check:
            url = site.get('url', '')
            is_alive, msg = self.check_site_alive(url)
            if is_alive:
                site['status'] = 'recovered'
                site['recovered_at'] = datetime.now().isoformat()
                self.new_recovered.append(site)
                self.recovered_sites.append({'url': url, 'name': site.get('name', ''),
                                             'domain': get_domain(url), 'recovered_at': datetime.now().isoformat()})
                self.dead_domains.discard(get_domain(url))
                print(f"  ✓ 恢复: {site.get('name', get_domain(url))} ({msg})")
            else:
                still_dead.append(site)
                print(f"  ✗ 仍失效: {site.get('name', get_domain(url))}")
            time.sleep(0.3)
        self.dead_sites = still_dead

    def _search_url_for_name(self, query: str, target_name: str) -> str:
        """通过搜索引擎查找站点URL"""
        for engine in ['bing', 'duckduckgo']:
            try:
                if engine == 'bing':
                    url = f'https://www.bing.com/search?q={quote(query)}&count=10'
                    ok, html = self.http_get(url, timeout=10)
                    if not ok:
                        continue
                    soup = BeautifulSoup(html, 'html.parser')
                    items = [(a.get('href', ''), a.get_text(strip=True)) for a in soup.select('h2 a') if a.get('href')]
                else:
                    url = f'https://html.duckduckgo.com/html/?q={quote(query)}'
                    ok, html = self.http_get(url, timeout=10)
                    if not ok:
                        continue
                    soup = BeautifulSoup(html, 'html.parser')
                    items = [(a.get('href', ''), a.get_text(strip=True)) for a in soup.select('a.result__a')
                           if a.get('href') and 'duckduckgo.com' not in a.get('href', '')]
                name_parts = re.sub(r'(API|中转站|中转|代理|转发)', '', target_name.lower()).strip()
                for href, title in items:
                    domain = get_domain(href)
                    if domain and len(domain) > 3 and name_parts:
                        if name_parts in domain or name_parts in href.lower():
                            return normalize_url(href)
                        if re.match(r'^[a-zA-Z0-9.-]+$', name_parts) and name_parts in domain:
                            return normalize_url(href)
            except:
                pass
        return ''

    def _extract_site_name(self, url: str, soup: BeautifulSoup, text: str) -> str:
        """从多个来源提取站点真实名称"""
        domain = get_domain(url)
        # 来源1: <title> 标签（最常见）
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        # 来源2: <h1> 标签（很多中转站首页有<h1>站点名称</h1>）
        h1 = ''
        for h1_tag in soup.find_all('h1'):
            t = h1_tag.get_text(strip=True)
            if t and len(t) < 40:
                h1 = t
                break
        # 来源3: <meta property="og:site_name"> 或 <meta name="application-name">
        og_name = ''
        for meta in soup.find_all('meta'):
            prop = meta.get('property', '') or meta.get('name', '')
            if prop in ('og:site_name', 'application-name', 'og:title'):
                content = meta.get('content', '').strip()
                if content and len(content) < 40:
                    og_name = content
                    break
        # 来源4: logo的alt文本
        logo_name = ''
        for img in soup.find_all('img'):
            alt = img.get('alt', '').strip()
            src = img.get('src', '').lower()
            cls = ' '.join(img.get('class', []))
            if ('logo' in src or 'logo' in cls or 'logo' in alt.lower()) and alt and len(alt) < 40:
                logo_name = alt
                break

        # 优先级：h1 > og:site_name > logo > title
        raw_name = h1 or og_name or logo_name or title or domain

        # 清理名称
        # 去掉常见后缀
        suffixes = [
            r'\s*[-|–—]\s*(首页|Home|登录|Login|注册|Sign|API|中转站|中转|代理|平台|官方|Official).*',
            r'\s*[-|–—_].*$',
            r'\s*(首页|Home|登录|Login|注册|Sign Up|API中转站|API中转|中转站|中转|代理平台).*$',
            r'\s*-\s*API.*$', r'\s*-\s*GPT.*$', r'\s*-\s*AI.*$',
            r'\s*API中转站.*$', r'\s*中转站.*$', r'\s*代理.*$',
        ]
        for pattern in suffixes:
            cleaned = re.sub(pattern, '', raw_name, flags=re.IGNORECASE).strip()
            if cleaned and len(cleaned) >= 2:
                raw_name = cleaned
                break

        # 去掉括号内容如 "(Beta)" "(测试)"
        raw_name = re.sub(r'\s*[(（][^)）]*[)）]\s*$', '', raw_name).strip()

        # 如果清理后太短或太长，回退到域名
        if len(raw_name) < 2 or len(raw_name) > 30:
            raw_name = domain

        return raw_name

    def _analyze_site_info(self, url: str) -> Dict:
        """爬取站点首页，提取信息并自动评分"""
        info = {
            'name': get_domain(url),
            'description': '',
            'models': ['multi'],
            'features': [],
            'score': 7.0,
            'response_time': None,
            'price': 'medium',
            'free_amount': '',
        }
        try:
            ok, html = self.http_get(url, timeout=10)
            if not ok:
                return info
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            text = soup.get_text(separator=' ')
            title = soup.title.string.strip() if soup.title else ''

            # 提取站点名称（多来源智能提取）
            info['name'] = self._extract_site_name(url, soup, text)

            # 提取描述（取前200字有意义的内容）
            text_clean = re.sub(r'\s+', ' ', text).strip()
            # 找包含关键词的句子
            sentences = re.split(r'[。！？.!?\n]', text_clean)
            desc_parts = []
            for s in sentences:
                s = s.strip()
                if len(s) > 10 and any(kw in s for kw in ['API', 'GPT', '模型', '中转', '代理', '低价', '稳定', '免费', '支持']):
                    desc_parts.append(s)
                    if len(''.join(desc_parts)) > 150:
                        break
            if desc_parts:
                info['description'] = ''.join(desc_parts)[:200]
            elif title:
                info['description'] = title

            # 检测支持的模型
            text_lower = text.lower()
            model_map = {
                'claude': ['claude', 'anthropic'],
                'gpt': ['gpt-4', 'gpt4', 'chatgpt', 'gpt-3.5'],
                'gemini': ['gemini'],
                'deepseek': ['deepseek'],
                'doubao': ['doubao', '豆包'],
                'qwen': ['qwen', '通义'],
                'kimi': ['kimi', 'moonshot'],
                'glm': ['chatglm', 'glm', '智谱'],
                'domestic': ['国产', '文心', '百度', '讯飞'],
            }
            detected_models = []
            for model, keywords in model_map.items():
                if any(kw in text_lower for kw in keywords):
                    detected_models.append(model)
            if detected_models:
                info['models'] = detected_models

            # 检测特性
            feature_map = {
                'cheap': ['低价', '便宜', '0.1', '0.5', '1元', '免费额度', '免费试用'],
                'stable': ['稳定', '可靠', 'SLA', '99.9%', '高可用'],
                'fast': ['快速', '低延迟', '毫秒', '高速'],
                'free': ['免费', '白嫖', '0元'],
                'multi': ['多模型', '全模型', '聚合'],
            }
            detected_features = []
            for feat, keywords in feature_map.items():
                if any(kw in text for kw in keywords):
                    detected_features.append(feat)
            if detected_features:
                info['features'] = detected_features

            # 检测免费额度
            free_match = re.search(r'(免费[^\d]*(\d+)[^\d]*[元额度天次]|新用户送[^\d]*(\d+)|注册送[^\d]*(\d+))', text)
            if free_match:
                info['free_amount'] = free_match.group(0)[:30]

            # 自动评分（基于检测到的信息）
            score = 7.0  # 基础分
            if detected_models:
                score += min(len(detected_models) * 0.3, 1.5)  # 多模型加分
            if 'stable' in detected_features:
                score += 0.5
            if 'fast' in detected_features:
                score += 0.3
            if 'cheap' in detected_features or 'free' in detected_features:
                score += 0.3
            if info['free_amount']:
                score += 0.3
            if info['description']:
                score += 0.3
            info['score'] = round(min(score, 9.99), 2)

            # 检测价格档次
            if any(kw in text for kw in ['低价', '便宜', '0.1倍', '1折', '按量']):
                info['price'] = 'low'
            elif any(kw in text for kw in ['企业级', '高端', '专属']):
                info['price'] = 'high'

        except Exception as e:
            print(f"      分析出错: {e}")

        return info

    # ---- 搜索发现 ----

    def _extract_urls_from_text(self, text: str, source_tag: str = '') -> List[Dict]:
        """从文本中提取所有可能是中转站的URL"""
        results = []
        for m in re.finditer(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text):
            found_domain = m.group(1).lower().replace('www.', '')
            found_url = normalize_url(m.group(0))
            if self.is_valid_station(found_url):
                results.append({'url': found_url, 'name': found_domain, 'domain': found_domain,
                                'description': '从文本提取', 'features': self._extract_features(text),
                                'source': f'{source_tag}_extract'})
        return results

    def _extract_features(self, text: str) -> List[str]:
        mapping = {'免费': 'free', '低价': 'cheap', '稳定': 'stable', 'claude': 'claude',
                   'gpt4': 'gpt4', 'gpt-4': 'gpt4', 'chatgpt': 'chatgpt', 'openai': 'openai',
                   'gemini': 'gemini', 'deepseek': 'deepseek', 'kimi': 'kimi',
                   'reseller': 'reseller', 'proxy': 'proxy', 'cheap': 'cheap'}
        text_lower = text.lower()
        return list({tag for kw, tag in mapping.items() if kw in text_lower})

    def _crawl_page_for_stations(self, page_url: str, source_tag: str) -> List[Dict]:
        """爬取页面全文，提取中转站URL"""
        results = []
        try:
            ok, html = self.http_get(page_url, timeout=12)
            if not ok:
                return results
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            text = soup.get_text(separator=' ')
            results.extend(self._extract_urls_from_text(text, source_tag))
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                if not href.startswith('http://') and not href.startswith('https://'):
                    continue
                clean_url = normalize_url(href)
                if self.is_valid_station(clean_url):
                    domain = get_domain(clean_url)
                    if not any(r.get('domain') == domain for r in results):
                        results.append({'url': clean_url, 'name': domain, 'domain': domain,
                                        'description': '从页面链接提取', 'features': self._extract_features(text[:500]),
                                        'source': f'{source_tag}_link'})
        except Exception as e:
            print(f"    爬取出错: {e}")
        return results

    def discover_new_sites(self):
        """搜索发现新站点：Bing文章→全文提取 + GitHub README + DuckDuckGo补充
        每日最多新增 MAX_NEW_SITES_PER_DAY 个站点，达到上限后停止搜索
        """
        # 先检查今日已有多少待审核站点（避免重复运行时超限）
        today = datetime.now().strftime('%Y-%m-%d')
        today_pending = [s for s in self.pending_stations
                         if s.get('status') == 'pending' and s.get('submitTime', '').startswith(today)]
        remaining_quota = MAX_NEW_SITES_PER_DAY - len(today_pending)
        if remaining_quota <= 0:
            print(f"\n{'='*50}")
            print(f"今日已发现 {len(today_pending)} 个新站点，已达上限 {MAX_NEW_SITES_PER_DAY}，跳过搜索")
            print(f"{'='*50}")
            return

        print(f"\n{'='*50}\n开始搜索发现新站点...（今日剩余额度: {remaining_quota}）\n{'='*50}")
        all_discovered = []
        seen_domains = set()

        # 强化排重：加载所有已知域名（index.html + pending + dead + stations_info.json）
        known_domains = set(self.existing_domains | self.pending_domains | self.dead_domains)
        try:
            stations_info_path = 'data/stations_info.json'
            if os.path.exists(stations_info_path):
                with open(stations_info_path, 'r', encoding='utf-8') as f:
                    for item in json.load(f):
                        url = item.get('url', '')
                        if url:
                            known_domains.add(get_domain(url))
                print(f"  排重域名池: {len(known_domains)} 个（含 stations_info.json）")
        except:
            pass

        def is_duplicate(domain: str) -> bool:
            """严格排重：主域名 + 子域名去重"""
            if domain in known_domains or domain in seen_domains:
                return True
            # 子域名去重：api.example.com 和 example.com 视为同一站点
            parts = domain.split('.')
            if len(parts) > 2:
                root = '.'.join(parts[-2:])
                if root in known_domains or root in seen_domains:
                    return True
            return False

        def check_quota() -> bool:
            """检查是否还有剩余额度"""
            return len(all_discovered) < remaining_quota

        # 第1步: Bing搜索文章 → 爬取全文提取URL
        print("  === 第1步：Bing搜索相关文章 ===")
        article_queries = [
            '"API中转站" 推荐 排行 -百科 -baike',
            '"ChatGPT API" 中转站 低价 稳定 -百科 -baike',
            '"OpenAI API" 中转 代理 推荐 -百科 -baike',
            '"ChatGPT API" proxy provider cheap',
            '"GPT-4 API" reseller provider list',
            'API中转站 推荐 site:zhihu.com',
            'ChatGPT API 中转 推荐 site:zhihu.com',
        ]
        article_urls = []
        for i, query in enumerate(article_queries):
            print(f"  [{i+1}/{len(article_queries)}] {query[:40]}...")
            try:
                ok, html = self.http_get(f'https://www.bing.com/search?q={quote(query)}&count=10', timeout=10)
                if ok:
                    soup = BeautifulSoup(html, 'html.parser')
                    for item in soup.select('li.b_algo'):
                        a_tag = item.select_one('h2 a')
                        if not a_tag:
                            continue
                        href = a_tag.get('href', '')
                        if not href or 'bing.com' in href or 'microsoft.com' in href:
                            continue
                        if get_domain(href) not in SKIP_SEARCH_DOMAINS and href not in article_urls:
                            article_urls.append(href)
            except:
                pass
            time.sleep(random.uniform(1, 2))
        print(f"  找到 {len(article_urls)} 篇文章")

        # 第2步: 爬取文章全文
        print(f"\n  === 第2步：爬取文章全文 ===")
        crawl_count = 0
        for i, article_url in enumerate(article_urls[:20]):
            if not check_quota():
                print(f"  已达今日额度上限 {MAX_NEW_SITES_PER_DAY}，停止搜索")
                break
            stations = self._crawl_page_for_stations(article_url, f'article:{i}')
            for s in stations:
                if is_duplicate(s['domain']):
                    continue
                if not check_quota():
                    break
                seen_domains.add(s['domain'])
                all_discovered.append(s)
                crawl_count += 1
                print(f"    ✓ {s['domain']}（剩余额度: {remaining_quota - len(all_discovered)}）")
            time.sleep(random.uniform(0.5, 1.5))
        print(f"  文章提取: {crawl_count} 个")

        # 第3步: GitHub搜索 README（最有效）
        print(f"\n  === 第3步：GitHub搜索 ===")
        github_count = 0
        for query in ['API中转站 推荐', 'ChatGPT API proxy China', 'OpenAI API 中转', 'AI API 中转站 列表']:
            if not check_quota():
                print(f"  已达今日额度上限 {MAX_NEW_SITES_PER_DAY}，停止搜索")
                break
            try:
                ok, html = self.http_get(f'https://github.com/search?q={quote(query)}&type=repositories', timeout=10)
                if ok:
                    soup = BeautifulSoup(html, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a.get('href', '')
                        if not re.match(r'^/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$', href):
                            continue
                        for branch in ['main', 'master']:
                            readme_url = f'https://raw.githubusercontent.com{href}/{branch}/README.md'
                            ok2, readme = self.http_get(readme_url, timeout=8)
                            if ok2:
                                for s in self._extract_urls_from_text(readme, f'github:{query[:8]}'):
                                    if is_duplicate(s['domain']):
                                        continue
                                    if not check_quota():
                                        break
                                    seen_domains.add(s['domain'])
                                    all_discovered.append(s)
                                    github_count += 1
                                    print(f"    ✓ {s['domain']}（剩余额度: {remaining_quota - len(all_discovered)}）")
                                break
                            time.sleep(0.5)
            except:
                pass
            time.sleep(random.uniform(1, 2))
        print(f"  GitHub提取: {github_count} 个")

        # 第4步: DuckDuckGo补充
        print(f"\n  === 第4步：DuckDuckGo补充 ===")
        ddg_count = 0
        for query in ['API中转站 推荐 排行', 'ChatGPT API proxy cheap reliable', 'AI API中转站 最新']:
            if not check_quota():
                print(f"  已达今日额度上限 {MAX_NEW_SITES_PER_DAY}，停止搜索")
                break
            try:
                ok, html = self.http_get(f'https://html.duckduckgo.com/html/?q={quote(query)}', timeout=10)
                if ok:
                    soup = BeautifulSoup(html, 'html.parser')
                    ddg_urls = []
                    for result in soup.select('.result'):
                        a_tag = result.select_one('a.result__a')
                        if not a_tag:
                            continue
                        href = a_tag.get('href', '')
                        if not href or 'duckduckgo.com' in href:
                            continue
                        if get_domain(href) not in SKIP_SEARCH_DOMAINS and href not in ddg_urls:
                            ddg_urls.append(href)
                    for article_url in ddg_urls[:5]:
                        if article_url in article_urls:
                            continue
                        if not check_quota():
                            break
                        for s in self._crawl_page_for_stations(article_url, f'ddg'):
                            if is_duplicate(s['domain']):
                                continue
                            if not check_quota():
                                break
                            seen_domains.add(s['domain'])
                            all_discovered.append(s)
                            ddg_count += 1
                            print(f"    ✓ {s['domain']}（剩余额度: {remaining_quota - len(all_discovered)}）")
                        time.sleep(0.5)
            except:
                pass
            time.sleep(random.uniform(1, 2))
        print(f"  DuckDuckGo提取: {ddg_count} 个")

        # 验证存活 + 爬取信息 + 自动评分
        print(f"\n  共 {len(all_discovered)} 个候选，验证存活并采集信息...")
        valid = []
        for site in all_discovered:
            domain = site.get('domain', '')
            url = site.get('url', '')
            is_alive, msg = self.check_site_alive(url)
            if is_alive:
                # 爬取站点首页提取信息
                print(f"  ✓ {domain} 存活，正在采集信息...", end='')
                site_info = self._analyze_site_info(url)
                # 合并信息
                site['name'] = site_info.get('name', site.get('name', domain))
                site['description'] = site_info.get('description', site.get('description', ''))
                site['models'] = site_info.get('models', ['multi'])
                site['features'] = site_info.get('features', [])
                site['score'] = site_info.get('score', 7.0)
                site['responseTime'] = site_info.get('response_time', '?')
                site['freeAmount'] = site_info.get('free_amount', '')
                valid.append(site)
                print(f" 评分:{site['score']} 模型:{site['models']}")
            else:
                print(f"  ✗ {domain} (不可访问)")
            time.sleep(0.3)

        if not valid:
            print(f"\n  未发现有效新站点")
            return

        # 转为前端格式（包含完整信息）
        for site in valid:
            item = {
                'name': site.get('name', site.get('domain', '')),
                'url': site.get('url', ''),
                'submitTime': datetime.now().isoformat(),
                'status': 'pending',
                'source': site.get('source', ''),
                'description': site.get('description', ''),
                'features': site.get('features', []),
                'models': site.get('models', ['multi']),
                'score': site.get('score', 7.0),
                'responseTime': site.get('responseTime', '?'),
                'freeAmount': site.get('freeAmount', ''),
                'checked_at': datetime.now().isoformat(),
                'check_count': 1,
            }
            self.pending_stations.append(item)
            self.pending_domains.add(site.get('domain', ''))
            self.new_discovered.append(item)

        # 自动审核：评分>7.5且存活检测通过的站点自动添加到approved
        self._auto_approve_pending()

    def _auto_approve_pending(self):
        """自动审核 pending 站点：评分>7.5且存活则自动通过"""
        import json, os
        pending_path = os.path.join(DATA_DIR, 'pending_stations.json')
        approved_path = os.path.join(DATA_DIR, 'approved_stations.json')
        
        if not os.path.exists(pending_path):
            return
        
        try:
            with open(pending_path, 'r', encoding='utf-8') as f:
                pending = json.load(f)
            
            if not isinstance(pending, list) or len(pending) == 0:
                return
            
            approved = []
            still_pending = []
            auto_approved = []
            
            for site in pending:
                # 自动审核规则：评分>7.5 且存活检测通过
                score = site.get('score', 0)
                alive = site.get('alive', False)
                url = site.get('url', '')
                
                if score > 7.5 and alive and url:
                    site['status'] = 'approved'
                    site['approved_at'] = datetime.now().isoformat()
                    site['approval_method'] = 'auto'
                    approved.append(site)
                    auto_approved.append(site.get('name', url))
                else:
                    still_pending.append(site)
            
            # 保存更新后的 pending
            with open(pending_path, 'w', encoding='utf-8') as f:
                json.dump(still_pending, f, ensure_ascii=False, indent=2)
            
            # 追加到 approved
            if approved:
                existing = []
                if os.path.exists(approved_path):
                    with open(approved_path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                
                existing_urls = {s.get('url', '') for s in existing}
                for site in approved:
                    if site.get('url', '') not in existing_urls:
                        existing.append(site)
                
                with open(approved_path, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
                
                print(f"[自动审核] {len(auto_approved)} 个站点自动通过: {', '.join(auto_approved)}")
        except Exception as e:
            print(f"[自动审核] 失败: {e}")

    # ---- 报告 ----

    def generate_report(self) -> Dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(time.time() - self.start_time, 1),
            'summary': {
                'total_existing': len(self.existing_domains),
                'total_existing_with_url': len(self.existing_stations),
                'total_pending': len(self.pending_stations),
                'total_dead': len(self.dead_sites),
                'new_discovered': len(self.new_discovered),
                'new_dead': len(self.new_dead),
                'new_recovered': len(self.new_recovered),
                'scrapling_available': HAS_SCRAPLING,
            },
            'new_discovered': [{'url': s.get('url', ''), 'name': s.get('name', ''), 'source': s.get('source', '')} for s in self.new_discovered],
            'new_dead': [{'url': s.get('url', ''), 'name': s.get('name', ''), 'reason': s.get('reason', '')} for s in self.new_dead],
            'new_recovered': [{'url': s.get('url', ''), 'name': s.get('name', '')} for s in self.new_recovered],
        }

    def run(self):
        self.start_time = time.time()
        print("=" * 60)
        print("API中转站爬虫 v9.0 精简版")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        self.init()
        self.load_all_data()
        self.check_existing_sites()
        self.check_dead_recovery()
        self.discover_new_sites()
        self.save_all_data()
        report = self.generate_report()
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        s = report['summary']
        print(f"\n{'='*60}\n爬虫完成! 耗时 {report['elapsed_seconds']} 秒")
        print(f"  已收录: {s['total_existing']} | 新失效: {s['new_dead']} | 恢复: {s['new_recovered']}")
        print(f"  新发现: {s['new_discovered']}/{MAX_NEW_SITES_PER_DAY} | 待审核: {s['total_pending']} | 失效: {s['total_dead']}")
        print(f"{'='*60}")
        return report


if __name__ == '__main__':
    try:
        SmartCrawler().run()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

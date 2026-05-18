#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中转站智能爬虫系统 v3.0
功能：
1. 多平台搜索（百度、知乎、抖音、小红书）
2. 新站点自动进入待审核队列
3. 自动检测失效站点并标记
4. 自动检测失效站点恢复
5. 智能评分排名
"""

import re
import json
import time
import random
import os
import sys
from urllib.parse import urlparse, quote
from datetime import datetime
from typing import List, Dict, Set

# 尝试导入Scrapling
try:
    from scrapling.fetchers import StealthyFetcher
    HAS_SCRAPLING = True
except ImportError:
    HAS_SCRAPLING = False
    print("Scrapling未安装，使用requests模式")

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ============ 配置 ============
SEARCH_KEYWORDS = [
    "API中转站", "AI API代理", "Claude API中转", "GPT API中转",
    "OpenAI中转", "API转发", "AI模型接口", "ChatGPT中转",
    "GPT4 API", "Claude3 API", "大模型API中转", "AI API转发"
]

EXCLUDE_DOMAINS = [
    'github.com', 'google.com', 'baidu.com', 'bilibili.com',
    'douyin.com', 'iesdouyin.com', 'xiaohongshu.com', 'zhihu.com', 
    'weibo.com', 'qq.com', 'wechat.com', 'aliyun.com', 'tencent.com',
    'vercel.app', 'netlify.app', 'github.io', 'cloudflare.com'
]

STATION_KEYWORDS = [
    'api', 'ai', 'gpt', 'claude', 'openai', 'forward', 'proxy',
    '中转', '代理', '转发', '模型', '接口', 'key'
]

# ============ 数据文件路径 ============
DATA_DIR = 'data'
STATIONS_FILE = f'{DATA_DIR}/stations.json'
PENDING_FILE = f'{DATA_DIR}/pending_stations.json'
DEAD_FILE = f'{DATA_DIR}/dead_sites.json'
REPORT_FILE = f'{DATA_DIR}/crawler_report.json'

class SmartAPICrawler:
    """智能API中转站爬虫"""
    
    def __init__(self):
        self.existing_urls: Set[str] = set()
        self.pending_urls: Set[str] = set()
        self.dead_urls: Set[str] = set()
        self.all_stations: List[Dict] = []
        self.pending_stations: List[Dict] = []
        self.dead_sites: List[Dict] = []
        self.new_discovered: List[Dict] = []
        self.new_recovered: List[Dict] = []
        self.new_dead: List[Dict] = []
        self.fetcher = None
        
    def load_all_data(self):
        """加载所有数据文件"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 加载已审核站点
        try:
            with open(STATIONS_FILE, 'r', encoding='utf-8') as f:
                self.all_stations = json.load(f)
                self.existing_urls = {s.get('url', '') for s in self.all_stations}
                print(f"  已加载 {len(self.all_stations)} 个已审核站点")
        except:
            self.all_stations = []
        
        # 加载待审核站点
        try:
            with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                self.pending_stations = json.load(f)
                self.pending_urls = {s.get('url', '') for s in self.pending_stations}
                print(f"  已加载 {len(self.pending_stations)} 个待审核站点")
        except:
            self.pending_stations = []
        
        # 加载失效站点
        try:
            with open(DEAD_FILE, 'r', encoding='utf-8') as f:
                self.dead_sites = json.load(f)
                self.dead_urls = {s.get('url', '') for s in self.dead_sites}
                print(f"  已加载 {len(self.dead_sites)} 个失效站点")
        except:
            self.dead_sites = []
    
    def save_all_data(self):
        """保存所有数据"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        with open(STATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.all_stations, f, ensure_ascii=False, indent=2)
        
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.pending_stations, f, ensure_ascii=False, indent=2)
        
        with open(DEAD_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.dead_sites, f, ensure_ascii=False, indent=2)
    
    def init_fetcher(self):
        """初始化爬虫"""
        if HAS_SCRAPLING:
            self.fetcher = StealthyFetcher()
            print("  Scrapling模式")
        else:
            print("  Requests模式")
    
    def is_valid_station_url(self, url: str) -> bool:
        """验证URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if not domain:
                return False
            
            # 检查是否已存在
            if domain in self.existing_urls or domain in self.pending_urls:
                return False
            
            # 排除已知平台
            for exclude in EXCLUDE_DOMAINS:
                if exclude in domain:
                    return False
            
            # 检查关键词
            combined = f"{domain} {parsed.path.lower()}"
            return any(kw in combined for kw in STATION_KEYWORDS)
        except:
            return False
    
    def extract_station_info(self, text: str, url: str, title: str = "", source: str = "") -> Dict:
        """提取站点信息"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        info = {
            'url': url,
            'name': domain,
            'domain': domain,
            'description': text[:200] if len(text) > 10 else title,
            'features': [],
            'source': source,
            'discovered_at': datetime.now().isoformat(),
            'status': 'pending',
            'checked_at': None,
            'check_count': 0
        }
        
        # 提取特征
        feature_map = {
            '免费': 'free', '低价': 'cheap', '稳定': 'stable', '快速': 'fast',
            'Claude': 'claude', 'GPT4': 'gpt4', 'GPT-4': 'gpt4', 'ChatGPT': 'chatgpt',
            'OpenAI': 'openai', '国内': 'china', '直连': 'direct'
        }
        
        for kw, tag in feature_map.items():
            if kw in text or kw in title:
                info['features'].append(tag)
        
        info['features'] = list(set(info['features']))
        return info
    
    def fetch_page(self, url: str, timeout: int = 15) -> tuple:
        """获取页面内容"""
        try:
            if HAS_SCRAPLING and self.fetcher:
                page = self.fetcher.fetch(url, stealthy_headers=True, timeout=timeout)
                return True, page
            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=timeout)
                return response.status_code == 200, response.text
        except Exception as e:
            return False, str(e)
    
    def search_baidu(self, keyword: str) -> List[Dict]:
        """百度搜索"""
        results = []
        try:
            url = f'https://www.baidu.com/s?wd={quote(keyword)}'
            success, content = self.fetch_page(url)
            
            if success and HAS_SCRAPLING:
                page = content
                for result in page.css('.result, .c-container'):
                    try:
                        title = result.css('h3 a').text() if result.css('h3 a') else ""
                        abstract = result.css('.abstract').text() if result.css('.abstract') else ""
                        href = result.css('h3 a').attr('href') if result.css('h3 a') else ""
                        
                        full_text = f"{title} {abstract}"
                        urls = re.findall(r'https?://[^\s<>"\']+', full_text)
                        if href:
                            urls.append(href)
                        
                        for u in urls:
                            if self.is_valid_station_url(u):
                                info = self.extract_station_info(full_text, u, title, 'baidu')
                                results.append(info)
                                print(f"      百度发现: {u}")
                    except:
                        continue
            time.sleep(random.uniform(2, 3))
        except Exception as e:
            print(f"    百度出错: {e}")
        return results
    
    def search_zhihu(self, keyword: str) -> List[Dict]:
        """知乎搜索"""
        results = []
        try:
            url = f'https://www.zhihu.com/search?type=content&q={quote(keyword)}'
            success, content = self.fetch_page(url)
            
            if success and HAS_SCRAPLING:
                page = content
                for item in page.css('.SearchResult-Card, .ContentItem')[:10]:
                    try:
                        title = item.css('.ContentItem-title').text() if item.css('.ContentItem-title') else ""
                        content_text = item.css('.RichContent-inner').text() if item.css('.RichContent-inner') else ""
                        
                        full_text = f"{title} {content_text}"
                        urls = re.findall(r'https?://[^\s<>"\']+', full_text)
                        
                        for u in urls:
                            if self.is_valid_station_url(u):
                                info = self.extract_station_info(full_text, u, title, 'zhihu')
                                results.append(info)
                                print(f"      知乎发现: {u}")
                    except:
                        continue
            time.sleep(random.uniform(2, 3))
        except Exception as e:
            print(f"    知乎出错: {e}")
        return results
    
    def search_douyin(self, keyword: str) -> List[Dict]:
        """抖音搜索 - 通过网页版"""
        results = []
        try:
            # 抖音网页版搜索
            url = f'https://www.douyin.com/search/{quote(keyword)}?type=video'
            print(f"    搜索抖音: {keyword}")
            
            # 抖音反爬很强，使用简单请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.douyin.com/'
            }
            
            if HAS_REQUESTS:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # 从页面提取链接
                    urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?', response.text)
                    
                    for u in urls:
                        if self.is_valid_station_url(u):
                            info = self.extract_station_info("", u, "", 'douyin')
                            results.append(info)
                            print(f"      抖音发现: {u}")
            
            time.sleep(random.uniform(3, 5))
        except Exception as e:
            print(f"    抖音出错: {e}")
        return results
    
    def search_xiaohongshu(self, keyword: str) -> List[Dict]:
        """小红书搜索"""
        results = []
        try:
            # 小红书网页版
            url = f'https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}'
            print(f"    搜索小红书: {keyword}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.xiaohongshu.com/'
            }
            
            if HAS_REQUESTS:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?', response.text)
                    
                    for u in urls:
                        if self.is_valid_station_url(u):
                            info = self.extract_station_info("", u, "", 'xiaohongshu')
                            results.append(info)
                            print(f"      小红书发现: {u}")
            
            time.sleep(random.uniform(3, 5))
        except Exception as e:
            print(f"    小红书出错: {e}")
        return results
    
    def check_site_alive(self, url: str) -> tuple:
        """检查站点是否可访问"""
        try:
            print(f"    检查: {url}")
            
            if HAS_SCRAPLING and self.fetcher:
                try:
                    page = self.fetcher.fetch(url, stealthy_headers=True, timeout=15)
                    title = page.css('title').text() if page.css('title') else ""
                    return True, title
                except:
                    return False, "无法访问"
            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                return response.status_code == 200, f"状态码: {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def check_existing_sites(self):
        """检查现有站点是否失效"""
        print("\n检查现有站点状态...")
        
        still_alive = []
        for site in self.all_stations:
            url = site.get('url', '')
            if not url:
                continue
            
            is_alive, msg = self.check_site_alive(url)
            site['checked_at'] = datetime.now().isoformat()
            site['check_count'] = site.get('check_count', 0) + 1
            
            if is_alive:
                still_alive.append(site)
                print(f"  ✓ 正常: {url}")
            else:
                # 标记为失效
                site['status'] = 'dead'
                site['dead_reason'] = msg
                site['dead_at'] = datetime.now().isoformat()
                self.dead_sites.append(site)
                self.new_dead.append(site)
                self.dead_urls.add(url)
                print(f"  ✗ 失效: {url} - {msg}")
            
            time.sleep(1)
        
        self.all_stations = still_alive
        self.existing_urls = {s.get('url', '') for s in still_alive}
    
    def check_dead_sites_recovery(self):
        """检查失效站点是否恢复"""
        print("\n检查失效站点恢复情况...")
        
        still_dead = []
        for site in self.dead_sites:
            url = site.get('url', '')
            if not url:
                continue
            
            is_alive, msg = self.check_site_alive(url)
            
            if is_alive:
                # 恢复为正常
                site['status'] = 'active'
                site['recovered_at'] = datetime.now().isoformat()
                site['recovered_reason'] = msg
                self.all_stations.append(site)
                self.existing_urls.add(url)
                self.new_recovered.append(site)
                print(f"  ✓ 恢复: {url}")
            else:
                still_dead.append(site)
                print(f"  ✗ 仍失效: {url}")
            
            time.sleep(1)
        
        self.dead_sites = still_dead
        self.dead_urls = {s.get('url', '') for s in still_dead}
    
    def discover_new_sites(self):
        """发现新站点"""
        print("\n开始搜索新站点...")
        
        all_discovered = []
        
        # 百度搜索
        print("  百度搜索...")
        for kw in SEARCH_KEYWORDS[:5]:
            results = self.search_baidu(kw)
            all_discovered.extend(results)
        
        # 知乎搜索
        print("  知乎搜索...")
        for kw in SEARCH_KEYWORDS[:3]:
            results = self.search_zhihu(kw)
            all_discovered.extend(results)
        
        # 抖音搜索
        print("  抖音搜索...")
        for kw in SEARCH_KEYWORDS[:2]:
            results = self.search_douyin(kw)
            all_discovered.extend(results)
        
        # 小红书搜索
        print("  小红书搜索...")
        for kw in SEARCH_KEYWORDS[:2]:
            results = self.search_xiaohongshu(kw)
            all_discovered.extend(results)
        
        # 去重并验证
        seen = set()
        for site in all_discovered:
            url = site.get('url', '')
            if url and url not in seen:
                seen.add(url)
                # 快速验证
                is_alive, _ = self.check_site_alive(url)
                if is_alive:
                    self.pending_stations.append(site)
                    self.pending_urls.add(url)
                    self.new_discovered.append(site)
                    print(f"  ✓ 新发现待审核: {url}")
                time.sleep(0.5)
    
    def generate_report(self) -> Dict:
        """生成报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_active': len(self.all_stations),
                'total_pending': len(self.pending_stations),
                'total_dead': len(self.dead_sites),
                'new_discovered': len(self.new_discovered),
                'new_recovered': len(self.new_recovered),
                'new_dead': len(self.new_dead)
            },
            'new_discovered': self.new_discovered,
            'new_recovered': self.new_recovered,
            'new_dead': self.new_dead
        }
    
    def run(self):
        """运行完整流程"""
        print("=" * 60)
        print("API中转站智能爬虫系统 v3.0")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.init_fetcher()
        self.load_all_data()
        
        # 1. 检查现有站点
        self.check_existing_sites()
        
        # 2. 检查失效站点恢复
        self.check_dead_sites_recovery()
        
        # 3. 发现新站点
        self.discover_new_sites()
        
        # 保存数据
        self.save_all_data()
        
        # 生成报告
        report = self.generate_report()
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 输出统计
        print("\n" + "=" * 60)
        print("爬虫完成!")
        print(f"  活跃站点: {report['summary']['total_active']}")
        print(f"  待审核: {report['summary']['total_pending']}")
        print(f"  失效站点: {report['summary']['total_dead']}")
        print(f"  新发现: {report['summary']['new_discovered']}")
        print(f"  新恢复: {report['summary']['new_recovered']}")
        print(f"  新失效: {report['summary']['new_dead']}")
        print("=" * 60)
        
        return report

def main():
    try:
        crawler = SmartAPICrawler()
        report = crawler.run()
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

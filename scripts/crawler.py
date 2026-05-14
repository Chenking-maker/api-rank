#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中转站自动爬虫
从抖音、小红书、百度、知乎、V2EX等平台搜索并提取中转站信息
"""

import re
import json
import time
import random
import hashlib
import os
import sys
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime

# 尝试导入需要的库
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("警告: requests/beautifulsoup4 未安装，将使用模拟数据")

# 尝试导入Selenium（用于抖音抓取）
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    print("警告: selenium 未安装，抖音抓取功能将受限")

# ============ 配置 ============
SEARCH_KEYWORDS = [
    "API中转站",
    "AI API代理", 
    "Claude API中转",
    "GPT API中转",
    "OpenAI中转",
    "API转发",
    "AI模型接口",
    "ChatGPT中转",
    "GPT4 API",
    "Claude3 API"
]

# 需要排除的域名
EXCLUDE_DOMAINS = [
    'github.com', 'google.com', 'baidu.com', 'bilibili.com',
    'douyin.com', 'iesdouyin.com', 'xiaohongshu.com', 'zhihu.com', 'weibo.com',
    'qq.com', 'wechat.com', 'aliyun.com', 'tencent.com',
    'vercel.app', 'netlify.app', 'github.io',
    'douyinvod.com', 'douyinpic.com', 'amemv.com',
    'xhscdn.com', 'xhslink.com',
]

# ============ 数据存储 ============
DATA_FILE = 'data/stations.json'

def load_existing_stations():
    """加载已存在的中转站数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_stations(stations):
    """保存中转站数据"""
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)

def extract_urls_from_text(text):
    """从文本中提取URL"""
    if not text:
        return []
    
    url_patterns = [
        r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
        r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
        r'[a-zA-Z0-9-]+\.(?:com|cn|net|org|io|app|xyz|top|cc|co)(?:/[^\s]*)?',
    ]
    
    urls = set()
    for pattern in url_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.strip()
            if not url.startswith('http'):
                url = 'https://' + url
            if any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.css', '.js']):
                continue
            urls.add(url)
    
    return list(urls)

def is_valid_station_url(url):
    """验证是否是有效的中转站URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            return False
        
        for exclude in EXCLUDE_DOMAINS:
            if exclude in domain:
                return False
        
        station_keywords = ['api', 'ai', 'gpt', 'claude', 'openai', 'forward', 
                          'proxy', '中转', '代理', '转发', '模型', '接口', 'key']
        
        if any(kw in domain for kw in station_keywords):
            return True
            
        return True
    except:
        return False

def extract_station_info(text, url):
    """从中转站相关文本中提取信息"""
    info = {
        'url': url,
        'name': '',
        'description': '',
        'features': []
    }
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        info['name'] = domain
        
        if text:
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 10:
                info['description'] = text[:200]
            
            feature_keywords = {
                '免费': 'free',
                '低价': 'cheap',
                '稳定': 'stable',
                '快速': 'fast',
                'Claude': 'claude',
                'GPT4': 'gpt4',
                'GPT-4': 'gpt4',
                'ChatGPT': 'chatgpt',
                'OpenAI': 'openai',
                '支持': 'support',
                '便宜': 'cheap'
            }
            
            for keyword, tag in feature_keywords.items():
                if keyword in text:
                    info['features'].append(tag)
    
    except Exception as e:
        print(f"提取信息出错: {e}")
    
    return info

# ============ 百度搜索 ============
def search_baidu(keyword):
    """百度搜索"""
    if not HAS_REQUESTS:
        return []
    
    results = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        search_url = f'https://www.baidu.com/s?wd={quote(keyword)}'
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.find_all(['div', 'article'], class_=re.compile(r'result|c-container')):
                title_elem = result.find(['h3', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    abstract_elem = result.find(['div', 'span'], class_=re.compile(r'content-right_|abstract'))
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''
                    
                    full_text = f"{title} {abstract}"
                    urls = extract_urls_from_text(full_text)
                    
                    for url in urls:
                        if is_valid_station_url(url):
                            info = extract_station_info(full_text, url)
                            info.update({
                                'source': 'baidu',
                                'keyword': keyword,
                                'discovered_at': datetime.now().isoformat()
                            })
                            results.append(info)
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"百度搜索出错: {e}")
    
    return results

# ============ 知乎搜索 ============
def search_zhihu(keyword):
    """知乎搜索"""
    if not HAS_REQUESTS:
        return []
    
    results = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        search_url = f'https://www.zhihu.com/api/v4/search_v3?t=general&q={quote(keyword)}'
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            
            for item in items:
                content = item.get('content', {})
                if content:
                    title = content.get('title', '') or content.get('question', {}).get('name', '')
                    excerpt = content.get('excerpt', '')
                    full_text = f"{title} {excerpt}"
                    
                    urls = extract_urls_from_text(full_text)
                    for url in urls:
                        if is_valid_station_url(url):
                            info = extract_station_info(full_text, url)
                            info.update({
                                'source': 'zhihu',
                                'keyword': keyword,
                                'discovered_at': datetime.now().isoformat()
                            })
                            results.append(info)
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"知乎搜索出错: {e}")
    
    return results

# ============ V2EX搜索 ============
def search_v2ex(keyword):
    """V2EX搜索"""
    if not HAS_REQUESTS:
        return []
    
    results = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        search_url = f'https://www.v2ex.com/search?q={quote(keyword)}'
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for topic in soup.find_all('div', class_='topic-item'):
                title_elem = topic.find('span', class_='topic-title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    urls = extract_urls_from_text(title)
                    
                    for url in urls:
                        if is_valid_station_url(url):
                            info = extract_station_info(title, url)
                            info.update({
                                'source': 'v2ex',
                                'keyword': keyword,
                                'discovered_at': datetime.now().isoformat()
                            })
                            results.append(info)
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"V2EX搜索出错: {e}")
    
    return results

# ============ 抖音搜索 ============
def search_douyin(keyword):
    """抖音搜索 - 使用Selenium"""
    if not HAS_SELENIUM:
        print("  未安装selenium，跳过抖音搜索")
        return []
    
    results = []
    driver = None
    
    try:
        print(f"  正在打开抖音搜索: {keyword}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
        search_url = f'https://www.douyin.com/search/{quote(keyword)}'
        driver.get(search_url)
        time.sleep(5)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-e2e="search-card-video"]'))
            )
        except:
            print("  等待超时，尝试继续解析")
        
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(2)
        
        videos = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="search-card-video"]')
        print(f"  找到 {len(videos)} 个视频")
        
        for video in videos[:10]:
            try:
                title_elem = video.find_element(By.CSS_SELECTOR, 'span[data-e2e="search-card-video-caption"]')
                title = title_elem.text if title_elem else ''
                
                author_elem = video.find_element(By.CSS_SELECTOR, 'span[data-e2e="search-card-video-username"]')
                author = author_elem.text if author_elem else ''
                
                full_text = f"{title} {author}"
                urls = extract_urls_from_text(full_text)
                
                for url in urls:
                    if is_valid_station_url(url):
                        info = extract_station_info(full_text, url)
                        info.update({
                            'source': 'douyin',
                            'keyword': keyword,
                            'discovered_at': datetime.now().isoformat(),
                            'author': author
                        })
                        results.append(info)
                        print(f"    发现: {url}")
                
            except:
                continue
        
        driver.quit()
        time.sleep(random.uniform(3, 5))
        
    except Exception as e:
        print(f"  抖音搜索出错: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return results

# ============ 小红书搜索 ============
def search_xiaohongshu(keyword):
    """小红书搜索 - 使用Selenium"""
    if not HAS_SELENIUM:
        print("  未安装selenium，跳过小红书搜索")
        return []
    
    results = []
    driver = None
    
    try:
        print(f"  正在打开小红书搜索: {keyword}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        search_url = f'https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}'
        driver.get(search_url)
        time.sleep(5)
        
        notes = driver.find_elements(By.CSS_SELECTOR, '.note-item, .feeds-page')
        
        for note in notes[:10]:
            try:
                title_elem = note.find_element(By.CSS_SELECTOR, '.title, .desc')
                title = title_elem.text if title_elem else ''
                
                urls = extract_urls_from_text(title)
                
                for url in urls:
                    if is_valid_station_url(url):
                        info = extract_station_info(title, url)
                        info.update({
                            'source': 'xiaohongshu',
                            'keyword': keyword,
                            'discovered_at': datetime.now().isoformat()
                        })
                        results.append(info)
                        print(f"    发现: {url}")
                
            except:
                continue
        
        driver.quit()
        time.sleep(random.uniform(3, 5))
        
    except Exception as e:
        print(f"  小红书搜索出错: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return results

# ============ 豆包搜索 ============
def search_doubao(keyword):
    """豆包搜索"""
    if not HAS_REQUESTS:
        return []
    
    results = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        
        search_url = f'https://www.doubao.com/search?q={quote(keyword)}'
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for elem in soup.find_all(['p', 'div', 'span']):
                text = elem.get_text(strip=True)
                urls = extract_urls_from_text(text)
                
                for url in urls:
                    if is_valid_station_url(url):
                        info = extract_station_info(text, url)
                        info.update({
                            'source': 'doubao',
                            'keyword': keyword,
                            'discovered_at': datetime.now().isoformat()
                        })
                        results.append(info)
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        print(f"豆包搜索出错: {e}")
    
    return results

# ============ 主函数 ============
def main():
    """主函数"""
    print("=" * 60)
    print("API中转站自动爬虫启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n依赖检查:")
    print(f"  requests/beautifulsoup4: {'已安装' if HAS_REQUESTS else '未安装'}")
    print(f"  selenium: {'已安装' if HAS_SELENIUM else '未安装'}")
    
    existing_stations = load_existing_stations()
    existing_urls = {s.get('url', '') for s in existing_stations}
    
    print(f"\n已有中转站: {len(existing_stations)} 个")
    
    new_stations = []
    
    # 1. 百度搜索
    print("\n开始百度搜索...")
    for keyword in SEARCH_KEYWORDS[:3]:
        print(f"  搜索: {keyword}")
        results = search_baidu(keyword)
        for r in results:
            if r['url'] not in existing_urls:
                new_stations.append(r)
                existing_urls.add(r['url'])
        time.sleep(random.uniform(2, 4))
    
    # 2. 知乎搜索
    print("\n开始知乎搜索...")
    for keyword in SEARCH_KEYWORDS[:2]:
        print(f"  搜索: {keyword}")
        results = search_zhihu(keyword)
        for r in results:
            if r['url'] not in existing_urls:
                new_stations.append(r)
                existing_urls.add(r['url'])
        time.sleep(random.uniform(2, 4))
    
    # 3. V2EX搜索
    print("\n开始V2EX搜索...")
    for keyword in SEARCH_KEYWORDS[:2]:
        print(f"  搜索: {keyword}")
        results = search_v2ex(keyword)
        for r in results:
            if r['url'] not in existing_urls:
                new_stations.append(r)
                existing_urls.add(r['url'])
        time.sleep(random.uniform(2, 4))
    
    # 4. 抖音搜索
    print("\n开始抖音搜索...")
    if HAS_SELENIUM:
        for keyword in SEARCH_KEYWORDS[:2]:
            print(f"  搜索: {keyword}")
            results = search_douyin(keyword)
            for r in results:
                if r['url'] not in existing_urls:
                    new_stations.append(r)
                    existing_urls.add(r['url'])
    else:
        print("  跳过（未安装selenium）")
    
    # 5. 小红书搜索
    print("\n开始小红书搜索...")
    if HAS_SELENIUM:
        for keyword in SEARCH_KEYWORDS[:1]:
            print(f"  搜索: {keyword}")
            results = search_xiaohongshu(keyword)
            for r in results:
                if r['url'] not in existing_urls:
                    new_stations.append(r)
                    existing_urls.add(r['url'])
    else:
        print("  跳过（未安装selenium）")
    
    # 6. 豆包搜索
    print("\n开始豆包搜索...")
    for keyword in SEARCH_KEYWORDS[:2]:
        print(f"  搜索: {keyword}")
        results = search_doubao(keyword)
        for r in results:
            if r['url'] not in existing_urls:
                new_stations.append(r)
                existing_urls.add(r['url'])
        time.sleep(random.uniform(2, 4))
    
    # 合并结果
    all_stations = existing_stations + new_stations
    
    # 保存数据
    save_stations(all_stations)
    
    print("\n" + "=" * 60)
    print(f"爬虫完成！")
    print(f"统计:")
    print(f"   - 原有站点: {len(existing_stations)} 个")
    print(f"   - 新发现: {len(new_stations)} 个")
    print(f"   - 总计: {len(all_stations)} 个")
    print(f"\n数据已保存到: {DATA_FILE}")
    print("=" * 60)
    
    # 输出GitHub Actions变量
    print(f"\n::set-output name=new_count::{len(new_stations)}")
    print(f"::set-output name=total_count::{len(all_stations)}")
    
    return len(new_stations)

if __name__ == '__main__':
    try:
        new_count = main()
        sys.exit(0 if new_count >= 0 else 1)
    except Exception as e:
        print(f"\n爬虫运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

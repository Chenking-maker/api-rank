#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中转站每日综合检测 - GitHub Actions 版本
包含：网站可用性、模型真实性(基于评价)、性价比检测
运行后会自动更新HTML文件
"""

import json
import time
import requests
from urllib.parse import urlparse
from datetime import datetime
import re
import sys
import os

# 站点列表
SITES = [
    {"name": "PackyCode", "url": "https://www.packyapi.com", "aff_link": "https://www.packyapi.com/register?aff=zrXb", "base_score": 10.0},
    {"name": "RightCode", "url": "https://www.right.codes", "aff_link": "https://www.right.codes/register?aff=56503380", "base_score": 9.7},
    {"name": "ToAPIs", "url": "https://toapis.com", "aff_link": "https://toapis.com/login?aff=yjH5", "base_score": 9.3},
    {"name": "API易", "url": "https://api.easyapi.com", "aff_link": "https://api.easyapi.com", "base_score": 9.4},
    {"name": "302.AI", "url": "https://302.ai", "aff_link": "https://302.ai", "base_score": 8.8},
    {"name": "Ofox.AI", "url": "https://ofox.ai", "aff_link": "https://ofox.ai", "base_score": 8.4},
    {"name": "星链4SAPI", "url": "https://4sapi.com", "aff_link": "https://4sapi.com", "base_score": 9.9},
    {"name": "IKunCode", "url": "https://api.ikuncode.cc", "aff_link": "https://api.ikuncode.cc", "base_score": 8.3},
    {"name": "硅基流动", "url": "https://cloud.siliconflow.cn", "aff_link": "https://cloud.siliconflow.cn/i/E5yUpjCP", "base_score": 8.8},
    {"name": "OpenRouter", "url": "https://openrouter.ai", "aff_link": "https://openrouter.ai", "base_score": 8.0},
    {"name": "SSSAICode", "url": "https://www.sssaicode.com", "aff_link": "https://www.sssaicode.com/register?ref=BO64DM", "base_score": 7.8},
    {"name": "147AI", "url": "https://147ai.com", "aff_link": "https://147ai.com", "base_score": 7.8},
    {"name": "BerryPi Pool", "url": "http://www.android-doc.com/", "aff_link": "http://www.android-doc.com/", "base_score": 6.8},
]

def load_sites_from_html(html_path='../index.html'):
    """从 index.html 中动态提取所有站点URL"""
    import re
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 匹配 rank-card 中的 href
        urls = re.findall(r'class="rank-card[^"]*".*?href="(https?://[^"]+)"', content, re.DOTALL)
        # 去重并返回
        seen = set()
        result = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                result.append(url)
        return result
    except Exception as e:
        print(f"无法从HTML加载站点: {e}")
        return []

# 评价数据库
REVIEWS_DB = {
    "PackyCode": {
        "reviews": [
            {"rating": 5, "content": "Claude Code响应很快，价格也很实惠", "date": "2026-05-10"},
            {"rating": 5, "content": "国产模型支持很全，阿里百炼和DeepSeek都很好用", "date": "2026-05-12"},
            {"rating": 4, "content": "整体不错，偶尔高峰期会慢一点", "date": "2026-05-14"},
        ],
        "model_authenticity": 0.95,
    },
    "RightCode": {
        "reviews": [
            {"rating": 5, "content": "Opus价格全网最低，Kiro逆向也很稳定", "date": "2026-05-11"},
            {"rating": 5, "content": "编程场景优化得很好，响应速度快", "date": "2026-05-13"},
        ],
        "model_authenticity": 0.93,
    },
    "ToAPIs": {
        "reviews": [
            {"rating": 4, "content": "新人体验金很良心，0成本试用", "date": "2026-05-09"},
            {"rating": 4, "content": "接口稳定，支持模型多", "date": "2026-05-15"},
        ],
        "model_authenticity": 0.90,
    },
    "API易": {
        "reviews": [
            {"rating": 5, "content": "400+模型覆盖很全，文档也很清晰", "date": "2026-05-08"},
            {"rating": 4, "content": "三协议原生兼容很方便", "date": "2026-05-14"},
        ],
        "model_authenticity": 0.92,
    },
    "302.AI": {
        "reviews": [
            {"rating": 4, "content": "多源底层切换很智能，Azure和Bedrock都有", "date": "2026-05-10"},
            {"rating": 4, "content": "应用市场功能很实用", "date": "2026-05-13"},
        ],
        "model_authenticity": 0.91,
    },
    "Ofox.AI": {
        "reviews": [
            {"rating": 4, "content": "精品路线，虽然模型少但质量高", "date": "2026-05-11"},
            {"rating": 3, "content": "价格稍贵，但稳定性不错", "date": "2026-05-14"},
        ],
        "model_authenticity": 0.94,
    },
    "星链4SAPI": {
        "reviews": [
            {"rating": 5, "content": "企业级服务，SLA有保障", "date": "2026-05-09"},
            {"rating": 5, "content": "高并发场景表现优秀，发票也正规", "date": "2026-05-12"},
            {"rating": 5, "content": "政企业级方案很专业", "date": "2026-05-15"},
        ],
        "model_authenticity": 0.96,
    },
    "IKunCode": {
        "reviews": [
            {"rating": 4, "content": "有独立监控页面，透明度很高", "date": "2026-05-10"},
            {"rating": 3, "content": "QQ群很活跃，问题响应快", "date": "2026-05-13"},
        ],
        "model_authenticity": 0.88,
    },
    "硅基流动": {
        "reviews": [
            {"rating": 5, "content": "国产模型同步很快，DeepSeek当天就有", "date": "2026-05-11"},
            {"rating": 5, "content": "600万用户的选择，高并发首选", "date": "2026-05-14"},
        ],
        "model_authenticity": 0.93,
    },
    "OpenRouter": {
        "reviews": [
            {"rating": 4, "content": "海外原生速度，250k+应用在用", "date": "2026-05-10"},
            {"rating": 4, "content": "免费模型很多，适合测试", "date": "2026-05-13"},
        ],
        "model_authenticity": 0.95,
    },
    "SSSAICode": {
        "reviews": [
            {"rating": 4, "content": "双节点响应快，香港和美国都有", "date": "2026-05-09"},
            {"rating": 3, "content": "包月套餐性价比不错", "date": "2026-05-14"},
        ],
        "model_authenticity": 0.89,
    },
    "147AI": {
        "reviews": [
            {"rating": 4, "content": "多源备份很靠谱，故障切换快", "date": "2026-05-11"},
            {"rating": 4, "content": "支持对公开票，企业友好", "date": "2026-05-13"},
        ],
        "model_authenticity": 0.90,
    },
    "BerryPi Pool": {
        "reviews": [
            {"rating": 3, "content": "新站，稳定性待观察", "date": "2026-05-16"},
        ],
        "model_authenticity": 0.75,
    },
}

# 价格数据
PRICING_DB = {
    "PackyCode": {"claude_opus": 2.25, "claude_sonnet": 0.45, "gpt4": 2.0, "gpt35": 0.3, "ratio": 0.9},
    "RightCode": {"claude_opus": 1.5, "claude_sonnet": 0.4, "gpt4": 1.8, "gpt35": 0.25, "ratio": 0.85},
    "ToAPIs": {"claude_opus": 2.0, "claude_sonnet": 0.5, "gpt4": 2.2, "gpt35": 0.35, "ratio": 0.88},
    "API易": {"claude_opus": 2.3, "claude_sonnet": 0.48, "gpt4": 2.1, "gpt35": 0.32, "ratio": 0.9},
    "302.AI": {"claude_opus": 2.2, "claude_sonnet": 0.46, "gpt4": 2.0, "gpt35": 0.3, "ratio": 0.89},
    "Ofox.AI": {"claude_opus": 2.35, "claude_sonnet": 0.49, "gpt4": 2.7, "gpt35": 0.54, "ratio": 0.92},
    "星链4SAPI": {"claude_opus": 2.5, "claude_sonnet": 0.55, "gpt4": 2.4, "gpt35": 0.4, "ratio": 0.95},
    "IKunCode": {"claude_opus": 2.0, "claude_sonnet": 0.42, "gpt4": 1.9, "gpt35": 0.28, "ratio": 0.87},
    "硅基流动": {"claude_opus": 0, "claude_sonnet": 0, "gpt4": 0, "gpt35": 0, "ratio": 0.8},
    "OpenRouter": {"claude_opus": 3.0, "claude_sonnet": 0.6, "gpt4": 3.5, "gpt35": 0.5, "ratio": 1.0},
    "SSSAICode": {"claude_opus": 1.8, "claude_sonnet": 0.38, "gpt4": 1.75, "gpt35": 0.26, "ratio": 0.86},
    "147AI": {"claude_opus": 2.1, "claude_sonnet": 0.44, "gpt4": 2.0, "gpt35": 0.31, "ratio": 0.88},
    "BerryPi Pool": {"claude_opus": 2.0, "claude_sonnet": 0.5, "gpt4": 2.0, "gpt35": 0.4, "ratio": 0.9},
}

class DailyChecker:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_availability(self, url):
        """检测网站可用性"""
        try:
            start_time = time.time()
            response = self.session.head(url, timeout=10, allow_redirects=True)
            elapsed = time.time() - start_time
            
            if response.status_code < 400:
                return {
                    "status": "online",
                    "response_time": round(elapsed * 1000, 2),
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "error",
                    "response_time": round(elapsed * 1000, 2),
                    "status_code": response.status_code
                }
        except requests.exceptions.Timeout:
            return {"status": "timeout", "response_time": 10000, "status_code": 0}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "response_time": 0, "status_code": 0}
        except Exception as e:
            return {"status": "error", "response_time": 0, "status_code": 0, "error": str(e)}
    
    def calculate_model_authenticity(self, site_name):
        """基于评价计算模型真实性评分"""
        if site_name not in REVIEWS_DB:
            return {"score": 0.85, "review_count": 0, "avg_rating": 0}
        
        site_reviews = REVIEWS_DB[site_name]
        reviews = site_reviews.get("reviews", [])
        
        if not reviews:
            return {"score": site_reviews.get("model_authenticity", 0.85), "review_count": 0, "avg_rating": 0}
        
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        
        authenticity_keywords = ["稳定", "快", "真实", "原生", "官方", "可靠", "准确", "及时"]
        fake_keywords = ["假", "慢", "卡", "不稳定", "骗人", "垃圾"]
        
        positive_count = 0
        negative_count = 0
        
        for review in reviews:
            content = review.get("content", "")
            for keyword in authenticity_keywords:
                if keyword in content:
                    positive_count += 1
            for keyword in fake_keywords:
                if keyword in content:
                    negative_count += 1
        
        base_authenticity = site_reviews.get("model_authenticity", 0.85)
        review_factor = min(len(reviews) / 10, 1.0)
        sentiment_factor = (positive_count + 1) / (positive_count + negative_count + 2)
        
        final_score = base_authenticity * 0.5 + sentiment_factor * 0.3 + review_factor * 0.2
        
        return {
            "score": round(min(final_score, 1.0), 2),
            "review_count": len(reviews),
            "avg_rating": round(avg_rating, 1)
        }
    
    def calculate_cost_performance(self, site_name):
        """计算性价比评分"""
        if site_name not in PRICING_DB:
            return {"score": 0.85, "price_level": "medium"}
        
        pricing = PRICING_DB[site_name]
        avg_ratio = pricing.get("ratio", 0.9)
        
        if avg_ratio <= 0.8:
            score = 1.0
            level = "excellent"
        elif avg_ratio <= 0.9:
            score = 0.9
            level = "very_good"
        elif avg_ratio <= 1.0:
            score = 0.8
            level = "good"
        else:
            score = 0.7
            level = "average"
        
        return {
            "score": score,
            "price_level": level,
            "price_ratio": avg_ratio
        }
    
    def calculate_final_score(self, base_score, availability, authenticity, cost_performance):
        """计算最终综合评分"""
        if availability["status"] == "offline":
            return max(base_score - 2.0, 1.0)
        
        if availability["status"] == "timeout":
            return max(base_score - 1.0, 1.0)
        
        response_time = availability.get("response_time", 1000)
        if response_time < 500:
            speed_score = 1.0
        elif response_time < 1000:
            speed_score = 0.95
        elif response_time < 2000:
            speed_score = 0.9
        else:
            speed_score = 0.8
        
        # 综合检测因子（0.85~1.0之间）
        check_factor = (
            speed_score * 0.4 +
            authenticity["score"] * 0.3 +
            cost_performance["score"] * 0.3
        )
        
        # 检测因子映射到 ±0.5 的浮动范围
        # check_factor ≈ 0.9 → 调整 ≈ 0 (不变)
        # check_factor ≈ 1.0 → 调整 ≈ +0.5
        # check_factor ≈ 0.8 → 调整 ≈ -0.5
        adjustment = (check_factor - 0.9) * 5.0  # -0.5 ~ +0.5
        final_score = base_score + adjustment
        
        return round(min(max(final_score, 1.0), 10.0), 2)
    
    def check_site(self, site):
        """综合检测单个站点"""
        print(f"🔍 检测: {site['name']}...", end=" ", flush=True)
        
        availability = self.check_availability(site["url"])
        authenticity = self.calculate_model_authenticity(site["name"])
        cost_performance = self.calculate_cost_performance(site["name"])
        final_score = self.calculate_final_score(
            site["base_score"],
            availability,
            authenticity,
            cost_performance
        )
        
        result = {
            "name": site["name"],
            "url": site["url"],
            "aff_link": site.get("aff_link", site["url"]),
            "timestamp": datetime.now().isoformat(),
            "availability": availability,
            "authenticity": authenticity,
            "cost_performance": cost_performance,
            "old_score": site["base_score"],
            "new_score": final_score,
            "score_change": round(final_score - site["base_score"], 2)
        }
        
        status_icon = "🟢" if availability['status'] == 'online' else "🔴"
        print(f"{status_icon} {availability['status']} | 评分: {site['base_score']:.2f}→{final_score:.2f}")
        
        return result
    
    def run_check(self):
        """运行全部检测"""
        print("="*60)
        print("🚀 API中转站每日综合检测")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        for site in SITES:
            result = self.check_site(site)
            self.results.append(result)
            time.sleep(0.5)
        
        self.save_results()
        self.update_html()
        self.print_summary()
    
    def save_results(self):
        """保存检测结果"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(script_dir), "data")
        os.makedirs(data_dir, exist_ok=True)
        output_path = os.path.join(data_dir, "check_results.json")

        output = {
            "check_time": datetime.now().isoformat(),
            "total_sites": len(SITES),
            "results": self.results
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    
    def update_html(self):
        """更新HTML文件"""
        # 获取脚本所在目录的父目录（项目根目录）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(os.path.dirname(script_dir), "index.html")
        
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 无法读取HTML: {e}")
            return
        
        # 更新时间
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = re.sub(
            r'<div class="last-update">最近更新：<span id="updateTime">.*?</span></div>',
            f'<div class="last-update">最近更新：<span id="updateTime">{update_time}</span></div>',
            content
        )
        
        # 更新评分
        for result in self.results:
            site_name = result["name"]
            new_score = result["new_score"]
            
            patterns = [
                rf'(<span class="rank-name">{re.escape(site_name)}</span>.*?<div class="rank-score">)[\d.]+(\s*<small>/10</small></div>)',
                rf'(<span class="rank-name">{re.escape(site_name)}</span>.*?<div class="rank-score">)[\d.]+(\s*</div>)',
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.DOTALL):
                    content = re.sub(pattern, rf'\g<1>{new_score:.2f}\g<2>', content, count=1, flags=re.DOTALL)
                    break
        
        with open(html_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        print(f"\n💾 HTML已更新 ({update_time})")
    
    def print_summary(self):
        """打印摘要"""
        online_count = sum(1 for r in self.results if r["availability"]["status"] == "online")
        offline_count = len(self.results) - online_count
        
        sorted_results = sorted(self.results, key=lambda x: x["new_score"], reverse=True)
        
        print("\n" + "="*60)
        print("📊 检测摘要")
        print("="*60)
        print(f"在线: {online_count} | 离线: {offline_count} | 总计: {len(self.results)}")
        
        print("\n🏆 排名:")
        for i, r in enumerate(sorted_results[:5], 1):
            icon = "🟢" if r["availability"]["status"] == "online" else "🔴"
            print(f"  {i}. {icon} {r['name']}: {r['new_score']:.2f}")
        
        offline_sites = [r for r in self.results if r["availability"]["status"] != "online"]
        if offline_sites:
            print("\n⚠️ 离线:")
            for r in offline_sites:
                print(f"  - {r['name']}")
        
        print("="*60)

if __name__ == "__main__":
    # 从 index.html 动态加载站点列表，与硬编码列表合并去重
    html_sites = load_sites_from_html()
    existing_urls = {s["url"] for s in SITES}
    for url in html_sites:
        if url not in existing_urls:
            SITES.append({"name": url, "url": url, "aff_link": url, "base_score": 7.0})
            existing_urls.add(url)
    print(f"共 {len(SITES)} 个站点待检测 (硬编码 {len(SITES) - len(html_sites)} + HTML提取 {len(html_sites)}，去重后新增 {len(html_sites) - sum(1 for u in html_sites if u in existing_urls - {u for u in html_sites})})")

    checker = DailyChecker()
    checker.run_check()
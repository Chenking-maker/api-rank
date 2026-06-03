#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中转站每周综合检测 - GitHub Actions 版本
包含：网站可用性、响应速度检测
运行后会自动更新 data/check_results.json 和 data/site_status.json
数据源：data/stations_info.json（所有站点）
"""

import json
import time
import requests
from datetime import datetime
import re
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

def load_sites_from_json():
    """从 stations_info.json 加载所有站点"""
    json_path = os.path.join(DATA_DIR, "stations_info.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            stations = json.load(f)
        if not isinstance(stations, list):
            print(f"错误: {json_path} 中的数据不是列表")
            return []
        # 只保留 alive=true 的站点（排除已标记失效的）
        valid_sites = []
        for s in stations:
            if s.get('alive', True):
                valid_sites.append({
                    "name": s.get('name', s.get('domain', '未知')),
                    "url": s.get('url', ''),
                    "domain": s.get('domain', ''),
                    "base_score": s.get('score', 7.0),
                })
        print(f"从 stations_info.json 加载了 {len(valid_sites)} 个有效站点")
        return valid_sites
    except FileNotFoundError:
        print(f"错误: 找不到 {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败 - {e}")
        return []
    except Exception as e:
        print(f"无法从JSON加载站点: {e}")
        return []

class WeeklyChecker:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_availability(self, url):
        """检测网站可用性和响应速度"""
        if not url or not url.startswith('http'):
            return {
                "status": "error",
                "response_time": 0,
                "status_code": 0,
                "error": "无效URL"
            }
        try:
            start_time = time.time()
            response = self.session.head(url, timeout=15, allow_redirects=True)
            elapsed = time.time() - start_time
            
            if response.status_code < 400:
                return {
                    "status": "online",
                    "response_time": round(elapsed * 1000, 2),
                    "status_code": response.status_code
                }
            else:
                # 尝试 GET 请求（有些站点 HEAD 不支持）
                start_time = time.time()
                response = self.session.get(url, timeout=15, allow_redirects=True, stream=True)
                response.close()
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
            return {"status": "timeout", "response_time": 15000, "status_code": 0}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "response_time": 0, "status_code": 0}
        except Exception as e:
            return {"status": "error", "response_time": 0, "status_code": 0, "error": str(e)}
    
    def calculate_speed_score(self, response_time):
        """根据响应速度计算评分（0-1）"""
        if response_time < 300:
            return 1.0
        elif response_time < 500:
            return 0.97
        elif response_time < 800:
            return 0.93
        elif response_time < 1000:
            return 0.88
        elif response_time < 1500:
            return 0.82
        elif response_time < 2000:
            return 0.75
        elif response_time < 3000:
            return 0.65
        else:
            return 0.5
    
    def calculate_final_score(self, base_score, availability):
        """根据可用性调整评分"""
        if availability["status"] == "offline":
            return max(base_score - 3.0, 1.0)
        if availability["status"] == "timeout":
            return max(base_score - 1.5, 1.0)
        if availability["status"] == "error":
            return max(base_score - 1.0, 1.0)
        
        speed_score = self.calculate_speed_score(availability.get("response_time", 1000))
        # 速度对评分的微调：±0.5
        adjustment = (speed_score - 0.85) * 3.33  # -0.5 ~ +0.5
        final_score = base_score + adjustment
        return round(min(max(final_score, 1.0), 10.0), 2)
    
    def check_site(self, site):
        """检测单个站点"""
        print(f"🔍 检测: {site['name']}...", end=" ", flush=True)
        
        availability = self.check_availability(site["url"])
        final_score = self.calculate_final_score(site["base_score"], availability)
        
        result = {
            "name": site["name"],
            "url": site["url"],
            "domain": site.get("domain", ""),
            "timestamp": datetime.now().isoformat(),
            "availability": availability,
            "old_score": site["base_score"],
            "new_score": final_score,
            "score_change": round(final_score - site["base_score"], 2)
        }
        
        status_icon = "🟢" if availability['status'] == 'online' else "🔴"
        print(f"{status_icon} {availability['status']} | 评分: {site['base_score']:.2f}→{final_score:.2f}")
        
        return result
    
    def run_check(self):
        """运行全部检测"""
        sites = load_sites_from_json()
        if not sites:
            print("没有站点需要检测")
            return
        
        print("="*60)
        print("🚀 API中转站每周综合检测")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 待检测站点: {len(sites)} 个")
        print("="*60)
        
        for site in sites:
            result = self.check_site(site)
            self.results.append(result)
            time.sleep(0.3)  # 避免请求过快
        
        self.save_results()
        self.update_site_status()
        self.sync_dead_sites()
        self.update_stations_info()
        self.print_summary()
    
    def save_results(self):
        """保存检测结果到 check_results.json"""
        os.makedirs(DATA_DIR, exist_ok=True)
        output_path = os.path.join(DATA_DIR, "check_results.json")
        
        output = {
            "check_time": datetime.now().isoformat(),
            "check_type": "weekly",
            "total_sites": len(self.results),
            "results": self.results
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 检测结果已保存到 check_results.json")
    
    def update_site_status(self):
        """更新 site_status.json（标记失效和恢复的站点）"""
        site_status_path = os.path.join(DATA_DIR, "site_status.json")
        
        new_dead = []
        recovered = []
        
        for result in self.results:
            if result["availability"]["status"] in ["offline", "timeout"]:
                new_dead.append({
                    "url": result["url"],
                    "name": result["name"],
                    "domain": result.get("domain", ""),
                    "reason": f"{result['availability']['status']} - 响应时间: {result['availability'].get('response_time', 0)}ms"
                })
            elif result["availability"]["status"] == "online":
                # 检查是否之前是失效的（从 daily_check_cache 或 site_status 中恢复）
                recovered.append({
                    "url": result["url"],
                    "name": result["name"],
                    "domain": result.get("domain", ""),
                    "recovered_at": datetime.now().isoformat()
                })
        
        status = {
            "updated_at": datetime.now().isoformat(),
            "recovered": recovered,
            "new_dead": new_dead
        }
        
        with open(site_status_path, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        print(f"💾 站点状态已更新 ({len(new_dead)} 个失效, {len(recovered)} 个在线)")
    
    def sync_dead_sites(self):
        """同步失效站点到 dead_sites.json"""
        dead_sites_path = os.path.join(DATA_DIR, "dead_sites.json")
        
        # 加载现有 dead_sites.json
        existing_dead = []
        try:
            with open(dead_sites_path, 'r', encoding='utf-8') as f:
                existing_dead = json.load(f)
            if not isinstance(existing_dead, list):
                existing_dead = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_dead = []
        
        # 提取已有域名的集合
        existing_domains = {s.get('domain', '') for s in existing_dead if s.get('domain')}
        
        # 从检测结果中提取失效站点
        new_dead_sites = []
        for result in self.results:
            if result["availability"]["status"] in ["offline", "timeout", "error"]:
                domain = result.get("domain", "")
                url = result["url"]
                # 从URL提取域名
                if not domain and url:
                    domain = re.sub(r'^https?://', '', url).split('/')[0].replace('www.', '')
                
                # 去重：基于域名
                if domain and domain not in existing_domains:
                    new_dead_sites.append({
                        "url": url,
                        "name": result["name"],
                        "domain": domain,
                        "status": "dead",
                        "detected_at": datetime.now().isoformat(),
                        "reason": f"{result['availability']['status']} - 响应时间: {result['availability'].get('response_time', 0)}ms"
                    })
                    existing_domains.add(domain)
        
        # 合并并保存
        combined = existing_dead + new_dead_sites
        with open(dead_sites_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已同步 {len(new_dead_sites)} 个新失效站点到 dead_sites.json (总计: {len(combined)})")
    
    def update_stations_info(self):
        """更新 stations_info.json 中的 alive 状态"""
        stations_path = os.path.join(DATA_DIR, "stations_info.json")
        
        try:
            with open(stations_path, 'r', encoding='utf-8') as f:
                stations = json.load(f)
            if not isinstance(stations, list):
                return
        except (FileNotFoundError, json.JSONDecodeError):
            return
        
        # 创建检测结果映射
        result_map = {}
        for r in self.results:
            url = r.get("url", "")
            domain = r.get("domain", "")
            if url:
                result_map[url] = r
            if domain:
                result_map[domain] = r
        
        updated_count = 0
        for station in stations:
            url = station.get("url", "")
            domain = station.get("domain", "")
            
            # 匹配检测结果
            matched = None
            if url and url in result_map:
                matched = result_map[url]
            elif domain and domain in result_map:
                matched = result_map[domain]
            
            if matched:
                old_alive = station.get("alive", True)
                new_alive = matched["availability"]["status"] == "online"
                
                if old_alive != new_alive:
                    station["alive"] = new_alive
                    station["last_check"] = datetime.now().strftime("%Y-%m-%d")
                    station["score"] = matched["new_score"]
                    updated_count += 1
        
        with open(stations_path, "w", encoding="utf-8") as f:
            json.dump(stations, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已更新 stations_info.json ({updated_count} 个站点状态变更)")
    
    def print_summary(self):
        """打印摘要"""
        online_count = sum(1 for r in self.results if r["availability"]["status"] == "online")
        offline_count = sum(1 for r in self.results if r["availability"]["status"] in ["offline", "timeout"])
        error_count = sum(1 for r in self.results if r["availability"]["status"] == "error")
        
        sorted_results = sorted(self.results, key=lambda x: x["new_score"], reverse=True)
        
        print("\n" + "="*60)
        print("📊 检测摘要")
        print("="*60)
        print(f"在线: {online_count} | 离线: {offline_count} | 错误: {error_count} | 总计: {len(self.results)}")
        
        print("\n🏆 评分前10:")
        for i, r in enumerate(sorted_results[:10], 1):
            icon = "🟢" if r["availability"]["status"] == "online" else "🔴"
            change = r["score_change"]
            change_str = f"({change:+.2f})" if change != 0 else ""
            print(f"  {i}. {icon} {r['name']}: {r['new_score']:.2f} {change_str}")
        
        offline_sites = [r for r in self.results if r["availability"]["status"] in ["offline", "timeout"]]
        if offline_sites:
            print("\n⚠️ 离线/超时站点:")
            for r in offline_sites:
                print(f"  - {r['name']} ({r['url']})")
        
        print("="*60)

if __name__ == "__main__":
    checker = WeeklyChecker()
    checker.run_check()

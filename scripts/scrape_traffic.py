"""
SimilarWeb 批量流量查询脚本
使用 Playwright 自动查询所有中转站的月访问量
输出 JSON 文件供 index.html 使用
"""

import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("请先安装 Playwright:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)


# ========== 配置 ==========
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "traffic_data.json"
STATIONS_FILE = Path(__file__).parent.parent / "data" / "stations_info.json"
INDEX_HTML = Path(__file__).parent.parent / "index.html"

# 每个站点查询间隔（秒），避免被反爬
DELAY_BETWEEN = 6
# 超时时间（毫秒）
TIMEOUT = 30000
# 最大重试次数
MAX_RETRIES = 2


def parse_visits(text: str) -> int | None:
    """将 '126.5K' / '1.2M' / '5.2B' 转换为整数"""
    if not text:
        return None
    text = text.strip().replace(",", "")
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.upper().endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return None
    try:
        return int(text)
    except ValueError:
        return None


async def scrape_site(page, domain: str) -> dict | None:
    """查询单个站点的 SimilarWeb 流量数据"""
    url = f"https://www.similarweb.com/website/{domain}/#overview"

    for attempt in range(MAX_RETRIES + 1):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)

            # 等待流量数据加载
            try:
                await page.wait_for_selector(
                    ".wa-summary__engagement-value",
                    timeout=15000
                )
            except Exception:
                # 可能需要更多时间加载
                await asyncio.sleep(3)

            # 提取数据
            result = await page.evaluate("""() => {
                const labels = document.querySelectorAll('.wa-summary__engagement-title');
                const values = document.querySelectorAll('.wa-summary__engagement-value');
                const data = {};

                for (let i = 0; i < labels.length && i < values.length; i++) {
                    const label = labels[i].textContent.trim();
                    const value = values[i].textContent.trim();
                    data[label] = value;
                }

                // 提取月份信息
                const titleEl = document.querySelector('h1');
                const titleText = titleEl ? titleEl.textContent : '';

                return {
                    labels_and_values: data,
                    page_title: titleText
                };
            }""")

            if not result or not result.get("labels_and_values"):
                if attempt < MAX_RETRIES:
                    print(f"  ⚠️  重试 {attempt + 1}/{MAX_RETRIES}...")
                    await asyncio.sleep(DELAY_BETWEEN)
                    continue
                return None

            data = result["labels_and_values"]
            title_text = result.get("page_title", "")

            # 提取月份
            month_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{4})', title_text)
            data_month = f"{month_match.group(1)} {month_match.group(2)}" if month_match else "Unknown"

            # 提取 Total Visits
            total_visits_text = data.get("Total Visits", "")
            total_visits = parse_visits(total_visits_text)

            # 提取 Bounce Rate
            bounce_rate = data.get("Bounce Rate", "N/A")

            # 提取 Pages per Visit
            pages_per_visit = data.get("Pages per Visit", "N/A")

            # 提取 Avg Visit Duration
            avg_duration = data.get("Avg Visit Duration", "N/A")

            return {
                "domain": domain,
                "total_visits": total_visits,
                "total_visits_display": total_visits_text,
                "bounce_rate": bounce_rate,
                "pages_per_visit": pages_per_visit,
                "avg_visit_duration": avg_duration,
                "data_month": data_month,
                "scraped_at": datetime.now().isoformat(),
            }

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  ⚠️  错误: {e}, 重试 {attempt + 1}/{MAX_RETRIES}...")
                await asyncio.sleep(DELAY_BETWEEN)
            else:
                print(f"  ❌ 最终失败: {e}")
                return None

    return None


async def main():
    # 读取站点列表
    stations = []
    if STATIONS_FILE.exists():
        with open(STATIONS_FILE, "r", encoding="utf-8") as f:
            stations = json.load(f)

    # 从 index.html 提取硬编码站点的域名（补充 stations_info.json 中没有的）
    if INDEX_HTML.exists():
        html_content = INDEX_HTML.read_text(encoding="utf-8")
        # 匹配 href="https://domain" 模式
        hardcoded_domains = set()
        for match in re.finditer(r'href="(https?://([^/"]+))"', html_content):
            domain = match.group(2)
            # 排除非站点链接
            skip_domains = [
                "github.com", "google.com", "claude.ai", "chatgpt.com",
                "similarweb.com", "cloudflare.com", "vercel.com", "netlify.com",
                "trae.cn", "mozilla.org", "w3.org", "linkedin.com", "twitter.com",
                "youtube.com", "reddit.com", "tiktok.com", "facebook.com",
                "instagram.com", "v2ex.com", "linux.do", "nodeseek.com",
            ]
            if not any(d in domain for d in skip_domains):
                hardcoded_domains.add(domain)

        # 合并域名列表
        existing_domains = {s.get("domain", "") for s in stations}
        for domain in hardcoded_domains:
            if domain not in existing_domains:
                stations.append({
                    "url": f"https://{domain}",
                    "domain": domain,
                    "name": domain,
                    "score": 0,
                })

    # 去重
    seen = set()
    unique_stations = []
    for s in stations:
        domain = s.get("domain", "")
        if domain and domain not in seen:
            seen.add(domain)
            unique_stations.append(s)
    stations = unique_stations

    print(f"📋 共 {len(stations)} 个站点待查询")
    print(f"⏱️  预计耗时: {len(stations) * DELAY_BETWEEN // 60} 分钟")
    print(f"📝 输出文件: {OUTPUT_FILE}")
    print()

    # 加载已有数据（断点续爬）
    existing_data = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_data = {item["domain"]: item for item in json.load(f)}
        print(f"✅ 已有 {len(existing_data)} 个站点的数据（将跳过）")
        print()

    results = []
    failed = []

    async with async_playwright() as p:
        # 启动浏览器（有头模式，方便观察进度）
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for i, station in enumerate(stations):
            domain = station.get("domain", "")
            name = station.get("name", domain)

            if not domain:
                continue

            # 跳过已有数据
            if domain in existing_data:
                results.append(existing_data[domain])
                continue

            print(f"[{i + 1}/{len(stations)}] 🔍 查询 {name} ({domain})...", end=" ", flush=True)

            data = await scrape_site(page, domain)

            if data:
                visits_display = data.get("total_visits_display", "N/A")
                visits_num = data.get("total_visits", 0)
                print(f"✅ {visits_display} ({data.get('data_month', '')})")
                results.append(data)
            else:
                print(f"❌ 查询失败")
                failed.append({"domain": domain, "name": name})

            # 间隔等待
            if i < len(stations) - 1:
                await asyncio.sleep(DELAY_BETWEEN)

        await browser.close()

    # 按流量排序
    results.sort(key=lambda x: x.get("total_visits") or 0, reverse=True)

    # 添加排名
    for i, item in enumerate(results):
        item["rank"] = i + 1

    # 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"✅ 查询完成！成功: {len(results)} 个，失败: {len(failed)} 个")
    print(f"📁 数据已保存到: {OUTPUT_FILE}")
    print()

    # 打印 TOP 20
    print("🏆 TOP 20 流量排行:")
    print("-" * 60)
    for item in results[:20]:
        visits = item.get("total_visits_display", "N/A")
        name = item.get("domain", "")
        month = item.get("data_month", "")
        print(f"  #{item['rank']:>2}  {visits:>10}/月  {name:<30} ({month})")

    if failed:
        print()
        print("❌ 查询失败的站点:")
        for item in failed:
            print(f"  - {item['name']} ({item['domain']})")

    print()
    print("💡 提示: 运行 python scripts/update_traffic_widget.py 可自动更新 index.html 中的排行榜")


if __name__ == "__main__":
    asyncio.run(main())

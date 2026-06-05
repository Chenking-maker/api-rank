"""
将 traffic_data.json 的数据更新到 index.html 的 3D 领奖台排行榜
自动替换 renderTrafficRank 函数中的硬编码数据
"""

import json
import re
from datetime import datetime
from pathlib import Path


INDEX_HTML = Path(__file__).parent.parent / "index.html"
TRAFFIC_DATA = Path(__file__).parent.parent / "data" / "traffic_data.json"


def parse_visits_to_display(visits: int) -> str:
    """将整数访问量转为显示格式"""
    if visits is None:
        return "N/A"
    if visits >= 1_000_000:
        return f"{visits / 1_000_000:.1f}M"
    if visits >= 1_000:
        return f"{visits / 1_000:.1f}K"
    return str(visits)


def get_data_month(data: list) -> str:
    """获取数据月份，转为中文格式"""
    if not data:
        return "未知"
    month = data[0].get("data_month", "Unknown")
    # 英文月份转中文
    month_map = {
        "January": "1月", "February": "2月", "March": "3月",
        "April": "4月", "May": "5月", "June": "6月",
        "July": "7月", "August": "8月", "September": "9月",
        "October": "10月", "November": "11月", "December": "12月",
    }
    for en, cn in month_map.items():
        if en in month:
            year_match = re.search(r'(\d{4})', month)
            year = year_match.group(1) if year_match else "2026"
            return f"{year}年{cn}"
    return month


def generate_traffic_js(data: list) -> str:
    """生成新的 trafficData 数组代码"""
    # 只取 TOP 5
    top5 = data[:5]

    lines = []
    lines.append("            const trafficData = [")
    for item in top5:
        name = item.get("domain", "").split(".")[0]
        # 尝试从 stations_info.json 获取中文名
        domain = item.get("domain", "")
        visits = item.get("total_visits", 0)
        lines.append(
            f'                {{ name: \'{name}\', domain: \'{domain}\', visits: {visits} }},'
        )
    lines.append("            ];")
    return "\n".join(lines)


def main():
    if not TRAFFIC_DATA.exists():
        print(f"❌ 找不到流量数据文件: {TRAFFIC_DATA}")
        print("   请先运行: python scripts/scrape_traffic.py")
        return

    if not INDEX_HTML.exists():
        print(f"❌ 找不到 index.html: {INDEX_HTML}")
        return

    with open(TRAFFIC_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("❌ 流量数据为空")
        return

    # 按流量排序
    data.sort(key=lambda x: x.get("total_visits") or 0, reverse=True)

    # 读取 index.html
    html = INDEX_HTML.read_text(encoding="utf-8")

    # 1. 替换 trafficData 数组
    old_pattern = r'(// SimilarWeb.*?\n\s*const trafficData = \[)(.*?)(\];)'
    new_js = generate_traffic_js(data)

    match = re.search(old_pattern, html, re.DOTALL)
    if not match:
        print("❌ 未找到 trafficData 数组，请检查 index.html 格式")
        return

    old_block = match.group(0)
    # 保留注释行
    comment_line = match.group(1).strip().split("\n")[0]
    new_block = f"{comment_line}\n{new_js}"

    html = html.replace(old_block, new_block)

    # 2. 更新数据来源说明中的月份
    data_month = get_data_month(data)
    old_month_pattern = r'SimilarWeb \d{4}年\d+月'
    new_month_text = f"SimilarWeb {data_month}"
    html = re.sub(old_month_pattern, new_month_text, html)

    # 3. 更新 TOP 5 显示文本（如果有的话）
    # 检查是否有 "TOP 5" 或 "TOP 10" 标记
    top_count = min(len(data), 10)
    # 不强制改，保持 TOP 5

    # 保存
    INDEX_HTML.write_text(html, encoding="utf-8")

    print(f"✅ 已更新 index.html 流量排行榜")
    print(f"📊 数据月份: {data_month}")
    print(f"🏆 TOP 5:")
    for item in data[:5]:
        visits = parse_visits_to_display(item.get("total_visits"))
        domain = item.get("domain", "")
        print(f"   #{item.get('rank', 0):>2}  {visits:>8}/月  {domain}")
    print()
    print(f"📝 共 {len(data)} 个站点有流量数据")
    print(f"💡 请刷新浏览器查看效果")


if __name__ == "__main__":
    main()

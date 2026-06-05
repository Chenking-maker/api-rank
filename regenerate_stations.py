# -*- coding: utf-8 -*-
import json
import re

# 从 index.html 提取的 #21-#64 卡片数据 (在当前版本中 HTML 只到 #20)
# 我们已经有了完整的 stations_info.json

# 读取现有的 stations_info.json
with open('data/stations_info.json', 'r', encoding='utf-8') as f:
    stations = json.load(f)

print(f"当前站点数量: {len(stations)}")

# 检查是否有 OpenRouter
has_openrouter = False
for s in stations:
    if 'openrouter' in s.get('domain', '').lower():
        has_openrouter = True
        break

print(f"是否已有 OpenRouter: {has_openrouter}")

# 如果缺少 OpenRouter，添加它
if not has_openrouter:
    openrouter_data = {
        "url": "https://openrouter.ai",
        "domain": "openrouter.ai",
        "name": "OpenRouter",
        "description": "全球最知名LLM API聚合商，60+Provider。a16z/Stripe引用，生态成熟可靠。",
        "models": ["claude", "gpt", "gemini"],
        "features": ["multi", "enterprise"],
        "price": "medium",
        "free_amount": "新用户$1免费",
        "score": 7.67,
        "response_time": 1.0,
        "alive": True,
        "last_check": "2026-06-02",
        "check_count": 1,
        "display_tags": ["海外原生", "250k+应用", "60+Provider"],
        "display_metrics": [
            {"label": "应用", "value": "全球聚合", "cls": "green"},
            {"label": "价格", "value": "按量付费", "cls": "accent"},
            {"label": "口碑", "value": "a16z引用", "cls": ""}
        ]
    }
    stations.append(openrouter_data)
    print("已添加 OpenRouter")

# 检查官方渠道完整性
official_channels = {
    "qianfan.baidubce.com": "百度千帆",
    "bigmodel.cn": "智谱AI",
    "volcengine.com": "豆包API",
    "platform.lingyiwanwu.com": "零一万物",
    "xinghuo.xfyun.cn": "讯飞星火",
    "bailian.console.aliyun.com": "通义千问",
    "openrouter.ai": "OpenRouter",
    "platform.deepseek.com": "DeepSeek API",
    "minimaxi.com": "MiniMax API",
    "dashboard.cohere.com": "Cohere",
    "console.groq.com": "Groq",
    "api.together.xyz": "Together AI",
    "fireworks.ai": "Fireworks AI",
    "deepinfra.com": "DeepInfra",
    "console.mistral.ai": "Mistral AI",
    "platform.baichuan-ai.com": "百川智能",
    "platform.moonshot.cn": "月之暗面",
    "closeai-asia.com": "CloseAI",
    "berrypi.com": "BerryPi Pool"
}

print("\n=== 官方渠道检查 ===")
for domain, name in official_channels.items():
    found = any(domain in s.get('domain', '') or s.get('url', '').find(domain) > 0 for s in stations)
    status = "✓" if found else "✗"
    print(f"  {status} {name} ({domain})")

# 标准化 domain 字段
for station in stations:
    url = station.get('url', '')
    if url:
        # 从 URL 中提取 domain
        match = re.search(r'https?://([^/]+)', url)
        if match:
            extracted_domain = match.group(1)
            # 移除 www. 前缀以保持一致性
            if extracted_domain.startswith('www.'):
                extracted_domain = extracted_domain[4:]
            station['domain'] = extracted_domain

# 排序: 按 score 降序
stations.sort(key=lambda x: x.get('score', 0), reverse=True)

# 添加 rank 字段
for i, station in enumerate(stations, 1):
    station['rank'] = i

print(f"\n最终站点数量: {len(stations)}")

# 写入文件 (UTF-8 编码)
with open('data/stations_info.json', 'w', encoding='utf-8') as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print("文件已保存为 UTF-8 编码")

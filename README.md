<p align="center">
  <img src="https://img.shields.io/badge/在线访问-api--rank--lake.vercel.app-blue?style=for-the-badge&logo=vercel" alt="Live Demo"/>
  <img src="https://img.shields.io/badge/收录平台-107+-green?style=for-the-badge" alt="Platforms"/>
  <img src="https://img.shields.io/badge/更新频率-每日-orange?style=for-the-badge" alt="Update Frequency"/>
  <img src="https://img.shields.io/badge/开源-YES-success?style=for-the-badge" alt="Open Source"/>
</p>

<h1 align="center">🏆 AI API中转站排行榜</h1>

<p align="center">
  <b>2026年最全面的AI大模型API平台评测与排行</b><br/>
  实时可用性检测 · 多维度评分 · 邀请链接优惠 · 完全开源
</p>

<p align="center">
  🔗 <a href="https://api-rank-lake.vercel.app">在线访问</a> · 
  📖 <a href="https://github.com/Chenking-maker/api-rank/wiki">使用文档</a> · 
  💬 <a href="https://github.com/Chenking-maker/api-rank/discussions">讨论区</a>
</p>

---

## ✨ 项目亮点

| 功能 | 说明 |
|------|------|
| 📊 **实时检测** | 自动检测各平台可用性，失效站点自动标记 |
| 🏅 **综合评分** | 稳定性、速度、价格、支持等多维度评分 |
| 🔍 **智能筛选** | 按模型类型（Claude/GPT/Gemini/国产）、价格、用途筛选 |
| 💰 **邀请优惠** | 整理各平台邀请链接，注册享额外优惠 |
| 🛡️ **商家后台** | 站长可提交站点、管理信息 |
| 📱 **响应式** | 完美适配PC和移动端 |
| 🔓 **开源** | 代码完全开源，数据透明 |

---

## 🏆 热门推荐（2026年6月）

| 排名 | 平台 | 评分 | 特色 | 邀请链接 |
|:----:|------|:----:|------|----------|
| 🥇 | **硅基流动** | 9.15 | 国产模型首选，DeepSeek全系，每日免费额度 | [访问](https://cloud.siliconflow.cn/i/E5yUpjCP) |
| 🥈 | **DeepSeek API** | 9.0 | 官方API，超低价，月免费额度 | [访问](https://platform.deepseek.com) |
| 🥉 | **OpenRouter** | 8.5 | 多模型聚合，新用户$1免费 | [访问](https://openrouter.ai) |
| 4 | **派客代码** | 8.5 | 多模型支持，稳定运营 | [访问](https://www.packyapi.com/register?aff=zrXb) |
| 5 | **豆包API** | 8.5 | 字节官方，企业支持 | [访问](https://www.volcengine.com) |
| 6 | **API2D** | 8.2 | 多模型，稳定运营，国内直连 | [访问](https://api2d.com) |
| 7 | **无限星河AI** | 8.2 | 92模型，验真检测，透明计费 | [访问](https://infistar.ai) |
| 8 | **灵芽API** | 8.0 | Claude/GPT专精，稳定低价 | [访问](https://api.lingyaai.cn/register?aff=k8I8) |
| 9 | **清沐API** | 8.0 | 智能调度，团队配额，负载均衡 | [访问](https://openqi.sbs) |
| 10 | **OpenModel AI** | 8.5 | 多模型LLM网关，按Token计费，无最低消费 | [访问](https://www.openmodel.ai?ref=MpYA6Pl5) |

> 完整排名请访问 [在线网站](https://api-rank-lake.vercel.app) 查看

---

## 🎯 支持的模型

| 类型 | 模型 |
|------|------|
| 🔵 **Claude** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 4 |
| 🟢 **GPT** | GPT-4o, GPT-5, o1, o3 |
| 🟡 **Gemini** | Gemini 2.5 Pro, Gemini 2.5 Flash |
| 🔴 **DeepSeek** | DeepSeek V3, DeepSeek R1, DeepSeek Coder |
| 🟣 **国产** | Qwen, Kimi, GLM, 豆包, 讯飞星火, 百川 |
| 🟠 **绘画** | Midjourney, Stable Diffusion, DALL-E |

---

## 📁 项目结构

```
api-rank/
├── index.html              # 首页（Top 20 + 动态加载）
├── all-stations.html       # 全部站点页面
├── admin.html              # 商家后台管理
├── dead-sites.html         # 失效站点列表
├── data/
│   ├── stations_info.json  # 主站点数据（107个）
│   ├── dead_sites.json     # 失效站点列表
│   ├── site_status.json    # 站点状态（恢复/新失效）
│   ├── daily_check_cache.json  # 每日检测缓存
│   └── approved_stations.json   # 审核通过的站点
├── scripts/
│   └── weekly_check.py     # 自动检测脚本
├── .github/
│   └── workflows/          # GitHub Actions
├── articles/               # 推广文章
│   ├── v2ex-promotion.md
│   ├── zhihu-article.md
│   └── twitter-thread.md
├── README.md
├── MAINTENANCE.md          # 维护指南
└── PROMOTION.md            # 推广方案
```

---

## 🚀 快速开始

### 在线使用
直接访问 [https://api-rank-lake.vercel.app](https://api-rank-lake.vercel.app)

### 本地部署
```bash
# 克隆仓库
git clone https://github.com/Chenking-maker/api-rank.git
cd api-rank

# 使用任意HTTP服务器
npx serve .
# 或
python -m http.server 8080
```

### Vercel部署
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
vercel
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| HTML5 + CSS3 | 页面结构与样式 |
| Vanilla JavaScript | 交互逻辑 |
| JSON | 数据存储 |
| GitHub Actions | 自动检测 |
| Vercel | 部署托管 |

---

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 收录平台 | 107+ |
| 有效站点 | 77 |
| 失效站点 | 30 |
| 支持模型类型 | 6+ |
| 更新频率 | 每日 |

---

## 🤝 贡献指南

欢迎各种形式的贡献！

### 提交新站点
1. Fork 本仓库
2. 编辑 `data/stations_info.json`，添加新站点
3. 提交 PR

### 报告失效站点
- 在 [Issues](https://github.com/Chenking-maker/api-rank/issues) 中提交
- 标题格式：`[失效报告] 站点名称 - 域名`

### 功能建议
- 在 [Discussions](https://github.com/Chenking-maker/api-rank/discussions) 中讨论

---

## 📝 更新日志

### v1.0.0 (2026-06-05)
- 🎉 首次正式发布
- ✅ 收录107个API中转站
- ✅ 实时可用性检测
- ✅ 综合评分排名系统
- ✅ XSS安全防护
- ✅ 响应式设计
- ✅ 商家后台管理
- ✅ GitHub Actions自动检测

---

## 📱 相关链接

- 🌐 **在线网站**: [https://api-rank-lake.vercel.app](https://api-rank-lake.vercel.app)
- 📖 **Wiki文档**: [https://github.com/Chenking-maker/api-rank/wiki](https://github.com/Chenking-maker/api-rank/wiki)
- 💬 **讨论区**: [https://github.com/Chenking-maker/api-rank/discussions](https://github.com/Chenking-maker/api-rank/discussions)
- 🐛 **问题反馈**: [https://github.com/Chenking-maker/api-rank/issues](https://github.com/Chenking-maker/api-rank/issues)

---

## 📄 许可证

MIT License

---

## 📝 免责声明

本项目仅提供信息汇总和评测，不构成任何投资建议。使用各API平台前请仔细阅读其服务条款。

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

Made with ❤️ for AI Developers

</div>

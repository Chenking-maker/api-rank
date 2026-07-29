<p align="center">
  <img src="https://img.shields.io/badge/在线访问-api--rank--lake.vercel.app-blue?style=for-the-badge&logo=vercel" alt="Live Demo"/>
  <img src="https://img.shields.io/badge/收录平台-118+-green?style=for-the-badge" alt="Platforms"/>
  <img src="https://img.shields.io/badge/更新频率-每日-orange?style=for-the-badge" alt="Update Frequency"/>
  <img src="https://img.shields.io/badge/开源-YES-success?style=for-the-badge" alt="Open Source"/>
</p>

<h1 align="center">🏆 AI API中转站排行榜</h1>

<p align="center">
  <b>2026年最全面的AI大模型API平台评测与排行</b><br/>
  实时可用性检测 · 多维度评分 · 邀请链接优惠 · 分享赚次数 · 完全开源
</p>

<p align="center">
  🔗 <a href="https://api-rank-lake.vercel.app">在线访问</a> ·
  📖 <a href="https://github.com/Chenking-maker/api-rank/wiki">使用文档</a> ·
  💬 <a href="https://github.com/Chenking-maker/api-rank/discussions">讨论区</a> ·
  🎨 <a href="https://api-rank-lake.vercel.app/creative-tools.html">AI绘图/视频专区</a>
</p>

---

## ✨ 项目亮点

| 功能 | 说明 |
|------|------|
| 📊 **实时检测** | 自动检测各平台可用性，失效站点自动标记 |
| 🏅 **综合评分** | 稳定性、速度、价格、支持等多维度评分（8.00-9.95分） |
| 🔍 **智能筛选** | 按模型类型（Claude/GPT/Gemini/国产/绘画/视频）、价格、用途筛选 |
| 💰 **邀请优惠** | 整理各平台邀请链接，注册享额外优惠 |
| 🔗 **分享赚次数** | 分享专属链接，好友注册即可获得额外查找次数 |
| 📱 **手机号绑定** | 国际化手机号绑定，换设备可恢复身份 |
| 🛡️ **商家后台** | 站长可提交站点、管理信息 |
| 📱 **响应式** | 完美适配PC和移动端 |
| 🔓 **开源** | 代码完全开源，数据透明 |

---

## 🏆 热门推荐（2026年7月）

| 排名 | 平台 | 评分 | 特色 | 邀请链接 |
|:----:|------|:----:|------|----------|
| 🥇 | **豆腐 (ToAPIs)** | 9.95 | 6大厂商官方授权，50+模型，视频模型 | [访问](https://toapis.com/login?aff=yjH5) |
| 🥈 | **派客代码** | 9.88 | 企业级AI控制台，7个全球PoP，99.9% SLA | [访问](https://www.packyapi.com/register?aff=zrXb) |
| 🥉 | **OpenRouter** | 9.85 | 400+模型，10M+用户，100T月Token | [访问](https://openrouter.ai) |
| 4 | **莱特代码** | 9.72 | 企业级Agent分发，99.5%可用率 | [访问](https://right.codes/register?aff=56503380) |
| 5 | **CoderPlan** | 9.68 | 多模型聚合，开发者友好 | [访问](https://coderplan.ai) |
| 6 | **硅基流动** | 9.62 | 国产模型首选，DeepSeek全系，每日免费额度 | [访问](https://cloud.siliconflow.cn/i/E5yUpjCP) |
| 7 | **红麦API** | 9.58 | 稳定运营，多模型支持 | [访问](https://hongmacc.com) |
| 8 | **RK API** | 9.55 | 高性价比，多渠道可选 | [访问](https://rkapi.com) |
| 9 | **无限星河AI** | 9.52 | 92模型，验真检测，透明计费 | [访问](https://infistar.ai) |
| 10 | **木瓜AI** | 9.48 | GPT-5.5特价，多分组渠道，Claude/GPT全系列 | [访问](https://api.mooko.ai/register?aff=JiqY) |

> 完整排名请访问 [在线网站](https://api-rank-lake.vercel.app) 查看

---

## 🎯 支持的模型

| 类型 | 模型 |
|------|------|
| 🔵 **Claude** | Claude 4 Opus, Claude 4 Sonnet, Claude 3.5 |
| 🟢 **GPT** | GPT-5.5, GPT-5, GPT-4o, o3, o1 |
| 🟡 **Gemini** | Gemini 3.1 Pro, Gemini 2.5 Pro, Gemini 2.5 Flash |
| 🔴 **DeepSeek** | DeepSeek V4, DeepSeek V3.2, DeepSeek R1 |
| 🟣 **国产** | GLM-5.2, Kimi K2.7, Qwen, 豆包, MiniMax M3 |
| 🟠 **绘画** | Midjourney, GPT-image-2, DALL-E, Stable Diffusion |
| 🎬 **视频** | Kling V3 Turbo, Veo, Sora2 |

---

## 📁 项目结构

```
api-rank/
├── index.html              # 首页（Top 20 + 动态加载 + 分享系统）
├── all-stations.html       # 全部站点页面
├── creative-tools.html      # AI绘图/视频专区
├── dead-sites.html          # 失效站点列表
├── data/
│   └── stations_info.json   # 主站点数据（118个）
├── api/                     # Cloudflare Workers 后端
│   ├── wrangler.toml        # Workers 配置
│   ├── schema.sql           # D1 数据库建表
│   └── src/
│       ├── index.js         # API 入口（注册/分享/次数管理）
│       └── utils.js         # JWT/工具函数
├── scripts/
│   └── weekly_check.py      # 自动检测脚本
├── .github/workflows/       # GitHub Actions
└── README.md
```

---

## 🚀 快速开始

### 在线使用
直接访问 [https://api-rank-lake.vercel.app](https://api-rank-lake.vercel.app)

### 本地部署
```bash
git clone https://github.com/Chenking-maker/api-rank.git
cd api-rank
npx serve .
```

### Vercel部署
```bash
npm i -g vercel
vercel
```

### 分享系统后端部署（可选）
```bash
cd api
npm install -g wrangler
wrangler login
wrangler d1 create api-rank-db  # 创建数据库
wrangler d1 execute api-rank-db --file=schema.sql  # 初始化表
wrangler secret put JWT_SECRET  # 设置JWT密钥
wrangler deploy  # 部署Workers
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| HTML5 + CSS3 | 页面结构与样式（暗色主题） |
| Vanilla JavaScript | 交互逻辑 |
| JSON | 数据存储 |
| Cloudflare Workers + D1 | 分享系统后端 |
| Web Crypto API | JWT 签发/验证 |
| GitHub Actions | 自动检测 |
| Vercel | 前端部署托管 |

---

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 收录平台 | 118+ |
| 有效站点 | 72 |
| 失效站点 | 46 |
| 支持模型类型 | 7+（含绘画/视频） |
| 评分范围 | 8.00 - 9.95 |
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

### v1.1.0 (2026-07-29)
- ✅ 新增分享赚次数系统（Cloudflare Workers后端）
- ✅ 新增API用户号自动注册（类似菩提苑）
- ✅ 新增国际化手机号绑定（20+国家/地区）
- ✅ 新增AI绘图/视频专区（creative-tools.html）
- ✅ 收录Seede AI、叮当次元袋、灵犀万相
- ✅ 全面重新评分（8.00-9.95分，拉开差距）
- ✅ 更新豆腐、派客代码、OpenRouter等站点描述
- ✅ 修复SSSAICode等失效站点数据

### v1.0.0 (2026-07-29)
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

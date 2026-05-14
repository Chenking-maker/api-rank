# API排行榜 - AI中转站性价比实时排行

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://api-rank-2025.github.io/api-rank/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black)](https://api-rank-lake.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 🤖 基于延迟、价格、稳定性、模型真实性等多维度自动测试，帮你快速筛选性价比最高的 AI API 中转服务

## 🌟 项目简介

API排行榜是一个开源的 AI API 中转站评测平台，通过自动化测试和社区众包数据，为用户提供客观、实时的中转站性能排行。

### 核心功能

- 📊 **实时排行** - 基于多维度评分的动态排行榜
- 🔍 **智能筛选** - 根据模型、预算、场景智能匹配最适合的中转站
- 📝 **自动收录** - 支持用户提交新站点，系统自动检测并评估
- 💀 **失效监测** - 标记已失效的API站点，避免用户踩坑
- 🎯 **精准推荐** - 针对Claude Code、GPT-4、Gemini等特定需求推荐

## 🚀 在线访问

- **GitHub Pages**: https://api-rank-2025.github.io/api-rank/
- **Vercel 镜像**: https://api-rank-lake.vercel.app

## 📋 收录站点

目前已收录 **64+** 个 API 中转站，包括：

- **国内主流**: 硅基流动、302.AI、诗云API、4ksAPI、星链4SAPI 等
- **国际平台**: OpenRouter、Together AI、DeepInfra 等
- **官方渠道**: 豆包(火山引擎)、DeepSeek、通义千问、Kimi 等
- **新兴平台**: 持续更新中...

## 🛠️ 技术栈

- **前端**: 纯 HTML5 + CSS3 + JavaScript (无框架依赖)
- **样式**: 自定义 CSS 变量 + 响应式设计
- **部署**: GitHub Pages + Vercel
- **自动化**: GitHub Actions (每日自动更新数据)

## 📁 项目结构

```
api-rank/
├── index.html          # 主页面 - 排行榜和核心功能
├── admin.html          # 管理后台 - 商家内部使用
├── scripts/
│   └── crawler.py      # 自动爬虫脚本 - 抓取新站点
├── .github/
│   └── workflows/
│       └── auto-update.yml  # GitHub Actions 自动更新
├── vercel.json         # Vercel 部署配置
└── README.md           # 项目说明
```

## 🎯 主要功能模块

### 1. 排行榜 (index.html)
- 64+ 中转站实时排行
- 6大评测维度：稳定性、速度、价格、支持、功能、真实性
- 智能标签筛选 (Claude/GPT/Gemini/国产/企业级等)
- 详细站点信息和直达链接

### 2. 智能匹配 (找适合自己的中转站)
- 根据使用模型推荐
- 根据预算范围筛选
- 根据使用场景匹配
- 根据特殊需求定制

### 3. 提交收录
- 用户可提交新站点
- 系统自动检测可用性
- IP地址和时间记录
- 管理员后台审核

### 4. 失效监测
- 标记已失效的API站点
- 显示失效时间和原因
- 灰色显示不可点击

## 🔄 自动更新

项目配置了 GitHub Actions 工作流，每天自动：

1. 运行爬虫脚本搜索新站点
2. 检测现有站点可用性
3. 更新排行榜数据
4. 提交变更到仓库

## 📝 提交新站点

如果你想提交新的 API 中转站：

1. 访问网站首页
2. 点击"提交收录"
3. 填写站点信息
4. 系统自动检测后会给出结果

或者直接在 GitHub 提交 Issue。

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue！

### 提交规范
- 提交新站点时请提供官方网站链接
- 说明站点支持的模型类型
- 如有测试数据请一并提供

## ⚠️ 免责声明

1. 本项目仅供技术交流和学习使用
2. 排行榜数据基于自动化测试和社区反馈，仅供参考
3. 使用 API 中转服务时请遵守相关法律法规
4. 建议小额测试后再进行大额充值

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

- GitHub: [@api-rank-2025](https://github.com/api-rank-2025)

## 🙏 致谢

感谢所有提交站点信息和反馈的用户！

---

> 💡 **提示**: 如果发现有站点失效或信息不准确，欢迎提交 Issue 反馈！
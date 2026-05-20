# API中转站排行榜

一个自动化的API中转站综合评测与排名网站，每天自动检测各站点的可用性、模型真实性和性价比。

## 🌐 在线访问

- **临时域名**: https://api-rank.370542303.workers.dev
- **自定义域名**: https://apirank.cn.eu.org (审核中)

## ✨ 功能特点

- 📊 **六维评分体系**: 稳定性、速度、价格、模型真实性、功能丰富度、文档质量
- 🤖 **每日自动检测**: 每天北京时间12:00自动检测所有站点
- 🔄 **实时更新**: 检测结果自动更新到网站
- 🔍 **智能匹配**: 根据用户需求推荐最适合的中转站
- 📱 **响应式设计**: 支持PC和移动端访问

## 🏆 当前排名

| 排名 | 名称 | 评分 | 特点 |
|------|------|------|------|
| 1 | PackyCode | 10.0 | Claude Code优化，国产模型支持全 |
| 2 | 星链4SAPI | 9.9 | 企业级服务，SLA保障 |
| 3 | RightCode | 9.7 | Opus价格最低，编程场景优化 |
| 4 | API易 | 9.4 | 400+模型，三协议原生兼容 |
| 5 | ToAPIs | 9.3 | 新人体验金，0成本试用 |

## 🛠️ 技术栈

- **前端**: HTML5 + Tailwind CSS + Vanilla JavaScript
- **部署**: Cloudflare Pages/Workers
- **自动化**: GitHub Actions
- **检测**: Python + Requests

## 🤖 自动化检测

### 检测维度

1. **网站可用性**: 响应时间、在线状态
2. **模型真实性**: 基于用户评价分析
3. **性价比**: 价格对比分析
4. **稳定性**: 历史可用率统计

### 运行方式

- **自动运行**: 每天北京时间12:00 (UTC 04:00)
- **手动触发**: 在 GitHub Actions 页面点击 "Run workflow"

### 本地运行

```bash
# 安装依赖
pip install requests

# 运行检测
python scripts/daily_check.py
```

## 📁 项目结构

```
.
├── .github/
│   └── workflows/
│       └── daily-check.yml    # GitHub Actions 工作流
├── scripts/
│   └── daily_check.py         # 检测脚本
├── index.html                 # 主页面
├── admin.html                 # 管理后台
├── check_results.json         # 检测结果
└── README.md                  # 项目说明
```

## 🔧 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets:

| Secret Name | 说明 | 获取方式 |
|------------|------|---------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Token | Cloudflare Dashboard → My Profile → API Tokens |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID | Cloudflare Dashboard 右侧栏 |

### 创建 Cloudflare API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击右上角头像 → My Profile
3. 选择 "API Tokens" 标签
4. 点击 "Create Token"
5. 选择 "Cloudflare Pages" 模板
6. 选择你的账户和项目
7. 创建并复制 Token

## 📝 更新日志

### 2026-05-17
- ✅ 添加 GitHub Actions 自动化工作流
- ✅ 实现每日自动检测和部署
- ✅ 添加 BerryPi Pool 到排行榜
- ⏳ 配置自定义域名 apirank.cn.eu.org

### 2026-05-16
- ✅ 移除推广服务功能
- ✅ 添加每月1次免费智能匹配
- ✅ 优化移动端体验

## 🤝 贡献

欢迎提交 Issue 和 PR 来改进这个项目！

## 📄 许可证

MIT License

## 📧 联系

如有问题或建议，欢迎通过以下方式联系：
- 在 GitHub 提交 Issue
- 邮件联系

---

**最后更新**: 2026-05-17 12:18

**检测状态**: ✅ 正常运行
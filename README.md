# API中转站排行榜

一个自动化的API中转站综合评测与排名网站，每周自动检测各站点的可用性、响应速度和性价比。

## 🌐 在线访问

- **主站**: https://api-rank.pages.dev
- **备用**: https://api-rank.370542303.workers.dev

## ✨ 功能特点

- 📊 **七维评分体系**: 稳定性、速度、价格、模型真实性、功能丰富度、文档质量、模型丰富度
- 🤖 **每周自动检测**: 每周一北京时间12:00自动检测所有站点
- 🔄 **实时更新**: 检测结果自动更新到网站
- 🔍 **智能匹配**: 根据用户需求推荐最适合的中转站
- 📱 **响应式设计**: 支持PC和移动端访问
- 🎯 **审核去重**: 自动过滤已收录/已拒绝的重复提交
- 📈 **流量排行**: 可视化展示热门中转站访问量

## 🏆 当前排名 TOP 10

| 排名 | 名称 | 评分 | 特点 |
|------|------|------|------|
| 1 | 诗云API | 9.50 | Claude Code优化，国产模型支持全 |
| 2 | 派客代码 (PackyCode) | 9.45 | Claude Code优化，上游供应商 |
| 3 | 莱特代码 (RightCode) | 9.40 | Opus价格最低，编程场景优化 |
| 4 | 星链4SAPI | 9.35 | 企业级服务，SLA保障 |
| 5 | 云雾API | 9.30 | 模型验真，透明计费 |
| 6 | 豆腐 (ToAPIs) | 9.20 | 新人体验金，0成本试用 |
| 7 | 木瓜AI | 9.15 | 多模型支持，稳定服务 |
| 8 | 硅基流动 | 9.10 | 国产模型全覆盖 |
| 9 | 302.AI | 9.05 | 功能丰富，企业友好 |
| 10 | 大模型API (DMXAPI) | 9.00 | 多协议兼容 |

> 完整排名请访问 [在线网站](https://api-rank.pages.dev)

## 📊 统计数据

- **收录站点**: 82+ 个中转站
- **有效站点**: ~79 个
- **失效站点**: ~3 个
- **检测周期**: 每周一 12:00 (北京时间)
- **评测维度**: 7 个维度综合评分

## 🛠️ 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **部署**: Cloudflare Pages
- **自动化**: GitHub Actions
- **检测**: Python + Requests

## 🤖 自动化检测

### 检测维度

1. **网站可用性**: HTTP响应状态、响应时间
2. **响应速度**: 分级评分（<300ms优秀，>3000ms较差）
3. **评分调整**: 根据可用性自动调整站点评分
4. **失效标记**: 自动标记离线/超时站点
5. **恢复检测**: 检测恢复的站点自动重新展示

### 运行方式

- **自动运行**: 每周一北京时间12:00 (UTC 04:00)
- **手动触发**: 在 GitHub Actions 页面点击 "Run workflow"

### 本地运行

```bash
# 安装依赖
pip install requests

# 运行检测
python scripts/weekly_check.py
```

## 📁 项目结构

```
.
├── .github/
│   └── workflows/
│       ├── deploy.yml           # 部署工作流
│       └── weekly-check.yml     # 每周检测工作流
├── scripts/
│   ├── weekly_check.py          # 每周检测脚本
│   └── daily_check.py           # 每日检测脚本（已弃用）
├── data/
│   ├── stations_info.json       # 站点数据（82个站点）
│   ├── check_results.json       # 检测结果
│   └── site_status.json         # 站点状态（失效/恢复）
├── index.html                   # 主页面
├── admin.html                   # 管理后台
├── dead-sites.html              # 失效站点列表
└── README.md                    # 项目说明
```

## 🔐 管理后台

访问 `/admin.html` 进入管理后台，功能包括：

- **收录审核**: 审核用户提交的中转站
- **爬虫数据**: 查看自动爬取的潜在站点
- **检测记录**: 查看每周检测结果
- **已拒绝列表**: 管理已拒绝的站点，支持撤销

### 审核去重机制

- 自动过滤已收录的站点
- 自动过滤已拒绝的站点
- 自动过滤审核队列中的重复提交
- 域名级去重（避免 www. 或路径差异）

## 🔧 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets:

| Secret Name | 说明 | 获取方式 |
|------------|------|---------|
| `CF_TOKEN` | Cloudflare API Token | Cloudflare Dashboard → My Profile → API Tokens |
| `CF_ACCOUNT_ID` | Cloudflare Account ID | Cloudflare Dashboard 右侧栏 |

### 创建 Cloudflare API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击右上角头像 → My Profile
3. 选择 "API Tokens" 标签
4. 点击 "Create Token"
5. 选择 "Cloudflare Pages" 模板
6. 选择你的账户和项目
7. 创建并复制 Token

## 📝 更新日志

### 2026-06-03
- ✅ 检测频率改为每周一次（更合理）
- ✅ 新增5个中转站（MFate AI、FreeModel、随人AI、XueDingToken、Kirby API）
- ✅ 完善审核去重机制（已拒绝/已收录自动过滤）
- ✅ 修复站点数量统计显示不一致问题
- ✅ 热门流量排行榜支持邀请链接跳转

### 2026-06-02
- ✅ 新增无限星河AI (infistar.ai)
- ✅ 修复官方渠道被黑名单拦截问题
- ✅ 修复评分超出范围问题（统一7.0-9.5）
- ✅ 新增审核管理后台
- ✅ 新增检测记录展示

### 2026-05-20
- ✅ 重构为动态加载（#1-#20硬编码，#21+从JSON加载）
- ✅ 新增云雾API、诗云API、清沐API
- ✅ 修复点赞按钮显示问题
- ✅ 修复评测维度数量（6→7）

### 2026-05-17
- ✅ 添加 GitHub Actions 自动化工作流
- ✅ 实现每日自动检测和部署

## 🤝 贡献

欢迎提交 Issue 和 PR 来改进这个项目！

### 提交新站点

1. 在网站首页点击"提交收录"
2. 填写中转站网址
3. 等待管理员审核

### 数据更新

站点数据存储在 `data/stations_info.json`，包含以下字段：

```json
{
  "url": "站点URL（含邀请链接）",
  "domain": "域名",
  "name": "站点名称",
  "description": "描述",
  "models": ["支持的模型类型"],
  "features": ["功能特点"],
  "display_tags": ["展示标签"],
  "display_metrics": [{"label": "标签", "value": "值", "cls": "样式类"}],
  "score": "评分（7.0-9.5）",
  "price": "价格等级（low/medium/high）",
  "response_time": "响应时间",
  "alive": "是否有效"
}
```

## 📄 许可证

MIT License

## 📧 联系

如有问题或建议，欢迎通过以下方式联系：
- 在 GitHub 提交 Issue
- 邮件联系

---

**最后更新**: 2026-06-03

**检测状态**: ✅ 正常运行 | **收录站点**: 82个 | **有效站点**: ~79个

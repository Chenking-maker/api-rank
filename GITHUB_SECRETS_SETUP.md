# GitHub Secrets 设置指南

## 需要添加的 Secrets

在 GitHub 仓库中，进入 Settings → Secrets and variables → Actions → New repository secret

### 1. GH_TOKEN
- **名称**: `GH_TOKEN`
- **值**: GitHub Personal Access Token
- **获取方式**: https://github.com/settings/tokens/new
  - Note: `API Rank Deploy`
  - 勾选权限: `repo` 和 `workflow`
  - 点击 Generate token
  - **立即复制保存（只显示一次）**

### 2. CF_TOKEN
- **名称**: `CF_TOKEN`
- **值**: Cloudflare API Token
- **获取方式**: Cloudflare Dashboard → My Profile → API Tokens
  - 点击 "Create Token"
  - 选择 "Cloudflare Pages" 模板
  - 点击 "Continue to summary"
  - 点击 "Create Token"
  - **立即复制保存（只显示一次）**

### 3. CF_ACCOUNT_ID
- **名称**: `CF_ACCOUNT_ID`
- **值**: Cloudflare Account ID
- **获取方式**: Cloudflare Dashboard 右侧边栏可以看到 Account ID

---

## 自动部署工作流

已创建两个工作流文件：

### 1. deploy.yml
- **触发**: 每次 push 到 main/master 分支时自动部署
- **功能**: 自动部署到 Cloudflare Pages

### 2. daily-check.yml
- **触发**: 每天北京时间 12:00 自动运行
- **功能**: 检测 API 中转站可用性并自动更新状态

---

## 验证部署

设置好 Secrets 后，可以通过以下方式触发部署：

1. **自动触发**: 推送代码到 main 分支
2. **手动触发**: 
   - 进入 GitHub 仓库 → Actions → Deploy to Cloudflare Pages
   - 点击 "Run workflow"

部署成功后，网站将自动更新到 Cloudflare Pages。

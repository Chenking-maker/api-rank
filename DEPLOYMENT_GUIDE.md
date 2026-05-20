# EdgeOne Pages + Cloudflare Pages 双部署指南

## 方案概述

采用双部署策略，实现全球最优访问：
- **国内用户** → 腾讯云 EdgeOne Pages（海外节点，速度中等）
- **海外用户** → Cloudflare Pages（全球 CDN，速度快）

## 部署步骤

### 1. Cloudflare Pages 部署（已配置）

已配置 GitHub Actions 自动部署到 Cloudflare Pages：
- 文件：`.github/workflows/deploy.yml`
- 触发：每次推送到 main 分支自动部署
- 域名：`api-rank.pages.dev`

### 2. 腾讯云 EdgeOne Pages 部署

#### 步骤 2.1：登录腾讯云 EdgeOne
1. 访问 https://console.cloud.tencent.com/edgeone
2. 使用微信/QQ/邮箱登录
3. 进入「边缘安全加速平台」

#### 步骤 2.2：创建 Pages 项目
1. 左侧菜单 → 「Pages」
2. 点击「新建项目」
3. 选择「从 GitHub 导入」
4. 授权并选择仓库：`api-rank-2025/api-rank`
5. 构建设置：
   - 框架预设：无
   - 构建命令：（留空，纯静态网站）
   - 输出目录：`.`
6. 点击「开始部署」

#### 步骤 2.3：绑定自定义域名（可选）
1. 部署完成后，进入项目设置
2. 选择「自定义域名」
3. 添加域名（如 `apirank.cn.eu.org`）
4. 按提示添加 DNS 记录

### 3. 双部署自动化（推荐）

修改 `.github/workflows/deploy.yml` 实现同时部署到两个平台：

```yaml
name: Deploy to EdgeOne + Cloudflare Pages

on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  deploy-cloudflare:
    name: Deploy to Cloudflare Pages
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Deploy to Cloudflare Pages
      uses: cloudflare/wrangler-action@v3
      with:
        apiToken: ${{ secrets.CF_TOKEN }}
        accountId: ${{ secrets.CF_ACCOUNT_ID }}
        command: pages deploy . --project-name=api-rank

  deploy-edgeone:
    name: Deploy to EdgeOne Pages
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Deploy to EdgeOne Pages
      run: |
        # 使用 EdgeOne CLI 或直接上传
        # 目前 EdgeOne Pages 支持 GitHub 自动同步，无需额外配置
        echo "EdgeOne Pages 会自动从 GitHub 同步更新"
```

### 4. DNS 分流配置（高级）

使用 DNS 解析实现智能分流：

| 用户位置 | 解析目标 |
|---------|---------|
| 中国大陆 | EdgeOne Pages 域名 |
| 海外 | Cloudflare Pages 域名 |

支持智能 DNS 的服务商：
- Cloudflare DNS（免费）
- DNSPod（免费）
- 阿里云 DNS（免费）

#### Cloudflare DNS 配置示例：

1. 在 Cloudflare 添加域名
2. 创建两条 A 记录：
   ```
   # 默认（海外用户）
   A  api-rank  CNAME  api-rank.pages.dev

   # 中国大陆用户（使用 EdgeOne）
   A  api-rank  CNAME  api-rank.edgeone.app  (仅限中国)
   ```

## 访问地址

部署完成后，网站可通过以下地址访问：

| 平台 | 地址 | 适用用户 |
|-----|------|---------|
| Cloudflare Pages | `https://api-rank.pages.dev` | 海外用户 |
| EdgeOne Pages | `https://api-rank.edgeone.app` | 国内用户 |
| 自定义域名 | `https://apirank.cn.eu.org` | 全部用户 |

## 注意事项

1. **EdgeOne Pages 免费额度**：
   - 流量：不限
   - 请求次数：不限
   - 构建次数：每月 500 次

2. **备案要求**：
   - EdgeOne Pages 海外节点无需备案
   - 如需使用中国大陆节点，需要 ICP 备案

3. **自动同步**：
   - EdgeOne Pages 支持 GitHub 自动同步
   - 每次推送到 main 分支，两个平台都会自动更新

## 监控和维护

- Cloudflare Dashboard: https://dash.cloudflare.com
- EdgeOne Dashboard: https://console.cloud.tencent.com/edgeone

## 故障排查

| 问题 | 解决方案 |
|-----|---------|
| EdgeOne 部署失败 | 检查 GitHub 授权是否过期 |
| 国内访问慢 | 确认 EdgeOne 节点是否生效 |
| 海外访问慢 | 检查 Cloudflare 部署状态 |
| 域名解析失败 | 检查 DNS 记录是否正确 |

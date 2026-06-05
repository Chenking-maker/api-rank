# 🔧 项目维护指南

## 📋 日常维护清单

### 每周检查
- [ ] 检查 `stations_info.json` 中是否有新失效站点
- [ ] 更新 `dead_sites.json`（添加新失效站点）
- [ ] 检查后台恢复的站点，确认是否已恢复
- [ ] 更新邀请链接（如有变化）

### 每月检查
- [ ] 全面检查所有站点可用性
- [ ] 更新评分（根据用户反馈和检测结果）
- [ ] 添加新发现的API中转站
- [ ] 检查并更新推广文章

---

## 🚀 快速操作命令

### 1. 添加新站点
编辑 `data/stations_info.json`，添加新站点对象：
```json
{
  "url": "https://example.com",
  "domain": "example.com",
  "name": "站点名称",
  "description": "站点描述",
  "models": ["gpt", "claude"],
  "features": ["stable", "multi"],
  "price": "low",
  "score": 8.0,
  "alive": true
}
```

### 2. 标记站点失效
在 `stations_info.json` 中：
```json
{
  "alive": false,
  "reason": "无法访问/域名出售/其他原因"
}
```

同时在 `dead_sites.json` 中添加：
```json
{
  "name": "站点名称",
  "domain": "example.com",
  "reason": "失效原因"
}
```

### 3. 推送更新到GitHub
```bash
git add .
git commit -m "描述修改内容"
git push
```

---

## 🐛 常见问题处理

### 问题1：首页显示站点数量不对
**原因**：`loadRecoveredFromAdmin` 或 `loadSiteStatus` 加载了已失效站点
**解决**：
1. 检查 `site_status.json` 的 `recovered` 数组
2. 清理 localStorage 中的 `recoveredSites`
3. 确保 `dead_sites.json` 包含所有失效域名

### 问题2：硬编码卡片和JSON数据不一致
**解决**：
1. 更新硬编码卡片的分数（与JSON中的 `score` 一致）
2. 为失效卡片添加 `dead` class
3. 更新排名编号

### 问题3：XSS漏洞报告
**解决**：
1. 确保所有用户输入都经过 `escapeHtml()` 处理
2. 使用 `textContent` 替代 `innerHTML` 插入纯文本

---

## 📝 推广渠道维护

### 已创建的文章
- `articles/v2ex-promotion.md` - V2EX社区推广
- `articles/zhihu-article.md` - 知乎文章
- `articles/twitter-thread.md` - Twitter推文串

### 发布平台
1. **V2EX** - 复制 `v2ex-promotion.md` 内容发布
2. **知乎** - 复制 `zhihu-article.md` 内容发布
3. **Twitter/X** - 按 `twitter-thread.md` 分5条发布
4. **掘金/segmentfault** - 技术文章

---

## 🔒 安全注意事项

1. **不要提交敏感信息**
   - 密码、Token等不要硬编码
   - 使用环境变量或配置文件（加入.gitignore）

2. **定期更新依赖**
   - 检查GitHub Actions工作流
   - 更新Node.js版本（如有）

3. **监控XSS漏洞**
   - 所有动态内容使用 `escapeHtml()`
   - 定期审查新添加的代码

---

## 📊 数据备份

重要数据文件：
- `data/stations_info.json` - 主站点数据
- `data/dead_sites.json` - 失效站点列表
- `data/site_status.json` - 站点状态

**备份策略**：
- Git自动备份（每次提交）
- 定期导出JSON备份

---

## 🤝 社区贡献

### 如何接收贡献
1. 在GitHub上开启Issues
2. 审查Pull Request
3. 定期合并更新

### 贡献者指南
1. Fork仓库
2. 创建特性分支
3. 提交PR
4. 等待审核

---

## 📈 效果追踪

### 关键指标
- GitHub Stars数
- 网站日访问量（Vercel Analytics）
- 各平台邀请链接点击量
- 新站点提交数量

### 追踪工具
- Vercel Analytics
- GitHub Insights
- 邀请链接统计（各平台后台）

---

## 🆘 紧急处理

### 网站被攻击
1. 立即检查 `index.html` 是否被篡改
2. 回滚到上一个稳定版本：`git revert HEAD`
3. 推送修复：`git push`

### 数据丢失
1. 从Git历史恢复：`git checkout <commit> -- data/`
2. 或从备份恢复

### 大量站点同时失效
1. 运行自动检测脚本
2. 批量更新 `dead_sites.json`
3. 发布公告说明情况

---

## 📞 联系方式

- GitHub Issues: https://github.com/Chenking-maker/api-rank/issues
- 项目主页: https://api-rank-lake.vercel.app

---

**最后更新**: 2026-06-05

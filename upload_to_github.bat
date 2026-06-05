@echo off
chcp 65001
echo ==========================================
echo  上传修改到 GitHub
echo ==========================================
echo.

cd /d "C:\Users\37054\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a08108c1bdac92eb4e95a79"

echo [1/4] 检查Git状态...
git status
echo.

echo [2/4] 添加所有修改的文件...
git add .
echo.

echo [3/4] 提交更改...
git commit -m "修复乱码、移除官方平台、更新排名和评分、优化后台功能

- 修复 approved_stations.json 乱码问题
- 移除16个官方平台和非API服务
- 更新61个中转站排名和评分
- 修复后台审核管理拒绝功能
- 修复工作流pip缓存问题
- 优化评分显示为2位小数"
echo.

echo [4/4] 推送到GitHub...
git push origin main
echo.

echo ==========================================
echo  上传完成！
echo ==========================================
pause

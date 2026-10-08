# GitHub 推送指南

> 一步步教你把这个项目推到你的 GitHub 仓库

---

## 第一步：在 GitHub 上创建新仓库

1. 打开 https://github.com/new
2. Repository name 填：`stanford-vibe-coding-cn`
3. Description 填：`Stanford Vibe Coding 课程中文翻译与管线项目`
4. 选 Public（公开）
5. **不要**勾选 "Add a README file"（因为我们已经有了）
6. 点击 Create repository

---

## 第二步：本地初始化 Git 并推送

在项目目录下执行：

```bash
# 进入项目目录
cd stanford-vibe-coding-cn

# 初始化 git
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "feat: Stanford Vibe Coding 课程中文翻译项目 v1.0

- 覆盖 4 门课程：CS146S、TECH 36 B、TECH 42、CS193T
- 完整翻译管线：抓取脚本 + 翻译分段 + 术语校验
- 交付物：README、AI日志、AAR复盘、使用指南
- 样章：CS146S Week 1 完整周次内容"

# 关联远程仓库（把下面的 URL 换成你自己的）
git remote add origin https://github.com/你的用户名/stanford-vibe-coding-cn.git

# 推送
git branch -M main
git push -u origin main
```

---

## 第三步：验证

推送成功后，打开你的 GitHub 仓库页面，应该能看到：
- README.md 自动渲染在首页
- 目录结构完整（source/ translated/ scripts/ config/）
- 所有 Markdown 文件正常显示

---

## 可选优化

### 加一个 LICENSE
```bash
# 在 GitHub 仓库页面 → Add file → Create new file
# 文件名填 LICENSE
# 选 MIT License 模板
```

### 加 GitHub Topics
在仓库首页右侧 → About 齿轮图标 → Topics 添加：
- `stanford`
- `vibe-coding`
- `translation`
- `ai`
- `education`

### 加一个 GitHub Pages 文档站（可选）
Settings → Pages → Source 选 main branch → 保存。
之后就能通过 `https://你的用户名.github.io/stanford-vibe-coding-cn/` 访问。

---

## 常见问题

**Q：push 的时候要密码怎么办？**
A：现在 GitHub 不用密码了，要用 Personal Access Token。去 Settings → Developer settings → Personal access tokens 生成一个，push 的时候当密码用。

**Q：报错 `remote origin already exists`？**
A：先执行 `git remote remove origin`，再重新 add。

**Q：不想公开怎么办？**
A：创建仓库的时候选 Private 就行。但挑战提交可能需要公开仓库，看具体要求。

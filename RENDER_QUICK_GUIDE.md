# 备份悟空52224 - Render.com 部署快速指南

## 📋 您的账号信息

- **邮箱**: 25285603@qq.com
- **密码**: 63iS$Tj5

---

## 🚀 部署步骤

### 步骤1: 安装 Git（如果未安装）

**Windows 安装 Git**:
1. 访问：https://git-scm.com/download/win
2. 下载 Windows 版本
3. 安装 Git（使用默认设置）
4. 验证安装：打开新的命令行窗口，运行 `git --version`

---

### 步骤2: 创建 GitHub 仓库

1. 访问：https://github.com/new
2. 登录您的 GitHub 账号
3. 填写仓库信息：
   - Repository name: `wukong-quant`
   - Description: `备份悟空52224 量化交易系统`
   - 选择 `Public` 或 `Private`
4. 点击 "Create repository"

---

### 步骤3: 初始化 Git 仓库

在项目目录中打开命令行：

```bash
# 进入项目目录
cd d:\trae\备份悟空52224

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit - 备份悟空52224"
```

---

### 步骤4: 连接 GitHub 仓库

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/wukong-quant.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**注意**: 首次推送时，GitHub 会要求您登录：
- Username: 您的 GitHub 用户名
- Password: 使用 GitHub Personal Access Token（不是密码）

**创建 Personal Access Token**:
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写：
   - Note: Render Deployment
   - Expiration: 选择过期时间
   - 勾选：repo（完整仓库访问权限）
4. 点击 "Generate token"
5. 复制生成的 token（只显示一次）

---

### 步骤5: 登录 Render.com

1. 访问：https://dashboard.render.com/register
2. 填写注册信息：
   - Email: `25285603@qq.com`
   - Password: `63iS$Tj5`
3. 点击 "Sign Up"
4. 验证邮箱（检查收件箱）

---

### 步骤6: 连接 GitHub 仓库

1. 登录 Render.com 后，点击 "New +"
2. 选择 "Web Service"
3. 在 "Connect a repository" 部分：
   - 选择 "GitHub"
   - 授权 Render 访问您的 GitHub
4. 找到 `wukong-quant` 仓库
5. 点击 "Connect"

---

### 步骤7: 配置 Web Service

**基本信息**:
- Name: `wukong-quant`
- Region: 选择离您最近的区域（如：Singapore）

**构建和部署**:
- Environment: `Python 3`
- Build Command: 留空（自动检测）
- Start Command: `python backend/app.py`

**环境变量**:
1. 点击 "Advanced" 展开
2. 点击 "Add Environment Variable"
3. 添加以下变量：
   - Key: `PORT`
   - Value: `5006`
   - 点击 "Add"

**实例类型**:
- Type: `Free`

---

### 步骤8: 部署应用

1. 点击底部的 "Create Web Service"
2. 等待自动部署（可能需要 3-5 分钟）
3. 查看部署日志

---

### 步骤9: 访问应用

1. 部署完成后，Render 会提供一个 URL
2. 点击 "URL" 链接访问应用
3. 访问登录页面：`https://wukong-quant.onrender.com/login.html`
4. 使用登录凭证：
   - 用户名: `admin`
   - 密码: `libo0519`

---

## 🔧 高级配置

### 配置自定义域名

1. 进入 Web Service 页面
2. 点击 "Custom Domains"
3. 点击 "Add Custom Domain"
4. 输入您的域名（如：wukong.yourdomain.com）
5. 配置 DNS 记录：
   - 类型: CNAME
   - 名称: wukong
   - 值: cname.render.com
6. 等待 DNS 生效（最多 24 小时）

### 配置持久化存储

Render 免费版不提供持久化存储，数据会在重启后丢失。

**解决方案**:
1. 使用外部数据库服务（如：Supabase、PlanetScale）
2. 升级到付费版（Starter $7/月）

### 配置自动休眠

Render 免费版会在 15 分钟无访问后自动休眠。

**解决方案**:
1. 使用 UptimeRobot 定期访问（免费）
   - 访问：https://uptimerobot.com
   - 添加监控：每 5 分钟访问一次
2. 升级到付费版

---

## 📊 监控和日志

### 查看部署日志

1. 进入 Web Service 页面
2. 点击 "Events" 标签
3. 查看部署历史和日志

### 查看应用日志

1. 进入 Web Service 页面
2. 点击 "Logs" 标签
3. 查看实时日志

### 查看应用状态

1. 进入 Web Service 页面
2. 查看顶部状态指示器
3. 绿色：运行中
4. 黄色：构建中
5. 红色：已停止

---

## 🔧 故障排查

### 问题1: 部署失败

**解决方法**:
1. 检查 `requirements.txt` 是否完整
2. 检查 Python 版本是否兼容
3. 查看部署日志
4. 检查 `Procfile` 是否正确

### 问题2: 应用无法启动

**解决方法**:
1. 检查启动命令是否正确
2. 检查环境变量是否设置
3. 查看应用日志
4. 检查端口配置

### 问题3: 应用休眠

**解决方法**:
1. 访问应用唤醒
2. 配置 UptimeRobot 定期访问
3. 升级到付费版

### 问题4: 数据丢失

**解决方法**:
1. 使用外部数据库
2. 定期备份数据
3. 升级到付费版

---

## 🎉 部署完成

您的应用现在已部署到 Render.com！

**访问地址**: `https://wukong-quant.onrender.com`

**登录凭证**:
- 用户名: `admin`
- 密码: `libo0519`

**重要提示**:
- ⚠️ 免费版会自动休眠
- ⚠️ 数据会在重启后丢失
- ⚠️ 冷启动需要 30-60 秒
- ⚠️ 升级到付费版可获得更好体验

---

## 📞 获取帮助

### 官方文档
- Render.com: https://render.com/docs
- GitHub: https://docs.github.com

### 社区支持
- Render Community: https://community.render.com
- Stack Overflow: 搜索 "render.com"

---

**祝您部署顺利！** 🚀
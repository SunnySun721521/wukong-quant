# 备份悟空52224 - Render.com 部署指南

## 📋 Render.com 简介

Render.com 是一个现代化的云服务平台，支持多种编程语言，非常适合部署 Web 应用。

**优点**:
- ✅ 完全免费
- ✅ 支持多种语言
- ✅ 自动部署（Git 集成）
- ✅ 自动 HTTPS
- ✅ 现代化界面
- ✅ 支持数据库

**缺点**:
- ⚠️ 免费版会休眠
- ⚠️ 冷启动较慢
- ⚠️ 有流量限制

**免费额度**:
- 无限 Web 服务
- 512MB RAM
- 750 小时/月
- 自动休眠（15分钟无访问）

---

## 🚀 部署步骤

### 步骤1: 注册账号

1. 访问：https://render.com
2. 点击右上角 "Sign Up"
3. 选择使用 GitHub 账号登录
4. 授权 Render 访问您的 GitHub
5. 验证邮箱

### 步骤2: 准备项目

**1. 初始化 Git 仓库**

在本地 PowerShell 中：
```powershell
cd d:\trae\备份悟空52224
git init
git add .
git commit -m "Initial commit"
```

**2. 创建 GitHub 仓库**

1. 访问：https://github.com/new
2. 输入仓库名称：`wukong-quant`
3. 选择 "Public" 或 "Private"
4. 点击 "Create repository"

**3. 推送到 GitHub**

在本地 PowerShell 中：
```powershell
git remote add origin https://github.com/yourusername/wukong-quant.git
git branch -M main
git push -u origin main
```

### 步骤3: 创建 Web Service

1. 登录 Render.com
2. 点击右上角 "New +"
3. 选择 "Web Service"

### 步骤4: 连接 GitHub 仓库

1. 在 "Connect a repository" 部分
2. 选择您的 GitHub 账号
3. 找到 `wukong-quant` 仓库
4. 点击 "Connect"

### 步骤5: 配置应用

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

### 步骤6: 部署应用

1. 点击底部的 "Create Web Service"
2. 等待自动部署（可能需要几分钟）
3. 查看部署日志

### 步骤7: 访问应用

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
6. 等待 DNS 生效

### 配置数据库

Render 提供免费的 PostgreSQL 数据库：

1. 点击 "New +"
2. 选择 "PostgreSQL"
3. 配置数据库
4. 在 Web Service 中添加环境变量：
   - Key: `DATABASE_URL`
   - Value: 复制数据库连接字符串

### 配置持久化存储

Render 免费版不提供持久化存储，数据会在重启后丢失。

解决方案：
1. 使用外部数据库服务（如：Supabase、PlanetScale）
2. 升级到付费版

### 配置自动休眠

Render 免费版会在 15 分钟无访问后自动休眠。

解决方案：
1. 使用外部服务定期唤醒（如：UptimeRobot）
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

## 📝 项目文件清单

确保您的项目包含以下文件：

```
备份悟空52224/
├── backend/
│   ├── app.py
│   ├── data/
│   └── ...
├── web/
│   ├── login.html
│   ├── index.html
│   └── ...
├── requirements.txt
├── Procfile
├── .gitignore
└── README.md
```

---

**祝您部署顺利！** 🚀
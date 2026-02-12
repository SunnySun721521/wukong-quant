# 备份悟空52224 - Render.com 部署步骤总结

## 📋 您的账号信息

- **邮箱**: 25285603@qq.com
- **密码**: 63iS$Tj5

---

## 🚀 快速部署步骤

### 第一步：安装 Git（必需）

1. **下载 Git**
   - 访问：https://git-scm.com/download/win
   - 下载：Git for Windows Setup

2. **安装 Git**
   - 运行安装程序
   - 使用默认设置
   - 点击 "Finish"

3. **验证安装**
   - 打开新的命令行窗口
   - 运行：`git --version`
   - 显示版本号说明安装成功

---

### 第二步：创建 GitHub 仓库

1. **访问 GitHub**
   - 访问：https://github.com/new
   - 登录您的 GitHub 账号

2. **创建仓库**
   - Repository name: `wukong-quant`
   - Description: `备份悟空52224 量化交易系统`
   - 选择：`Public` 或 `Private`
   - 点击：`Create repository`

3. **创建 Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击：`Generate new token (classic)`
   - Note: `Render Deployment`
   - Expiration: 选择 `No expiration` 或 90 天
   - 勾选：`repo`（完整仓库访问权限）
   - 点击：`Generate token`
   - **重要**：复制生成的 token（只显示一次）

---

### 第三步：初始化 Git 仓库

在项目目录中打开命令行（CMD 或 PowerShell）：

```bash
# 进入项目目录
cd d:\trae\备份悟空52224

# 初始化 Git 仓库
git init

# 配置用户信息（替换为您的信息）
git config user.name "Your Name"
git config user.email "25285603@qq.com"

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit - 备份悟空52224"
```

---

### 第四步：推送到 GitHub

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/wukong-quant.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**注意**：推送时，GitHub 会要求您输入凭证：
- Username: 您的 GitHub 用户名
- Password: 粘贴刚才创建的 Personal Access Token（不是密码）

---

### 第五步：登录 Render.com

1. **访问 Render**
   - 访问：https://dashboard.render.com/login
   - 输入邮箱：`25285603@qq.com`
   - 输入密码：`63iS$Tj5`
   - 点击：`Log in`

2. **验证邮箱**
   - 检查邮箱收件箱
   - 点击验证链接（如需要）

---

### 第六步：创建 Web Service

1. **创建新服务**
   - 登录后，点击右上角 `New +`
   - 选择：`Web Service`

2. **连接 GitHub 仓库**
   - 在 `Connect a repository` 部分
   - 选择：`GitHub`
   - 授权 Render 访问您的 GitHub
   - 找到：`wukong-quant` 仓库
   - 点击：`Connect`

3. **配置应用**
   - Name: `wukong-quant`
   - Region: 选择离您最近的区域（如：Singapore）
   - Environment: `Python 3`
   - Build Command: 留空（自动检测）
   - Start Command: `python backend/app.py`

4. **添加环境变量**
   - 点击 `Advanced` 展开
   - 点击 `Add Environment Variable`
   - 添加：
     - Key: `PORT`
     - Value: `5006`
   - 点击：`Add`

5. **选择实例类型**
   - Type: `Free`

6. **创建服务**
   - 点击底部的 `Create Web Service`
   - 等待自动部署（可能需要 3-5 分钟）

---

### 第七步：访问应用

1. **获取应用 URL**
   - 部署完成后，Render 会提供一个 URL
   - 格式：`https://wukong-quant.onrender.com`

2. **访问应用**
   - 点击 `URL` 链接访问应用
   - 或直接在浏览器中打开：`https://wukong-quant.onrender.com/login.html`

3. **登录系统**
   - 用户名：`admin`
   - 密码：`libo0519`

---

## 📁 项目文件清单

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

**重要文件**：
- ✅ `requirements.txt` - Python 依赖列表
- ✅ `Procfile` - 启动命令
- ✅ `.gitignore` - Git 忽略文件

---

## 🔧 故障排查

### 问题1：Git 未安装

**解决方法**：
1. 访问：https://git-scm.com/download/win
2. 下载并安装 Git
3. 验证：`git --version`

### 问题2：GitHub 推送失败

**可能原因**：
- 未创建 Personal Access Token
- Token 权限不足
- 用户名或密码错误

**解决方法**：
1. 检查 Token 是否正确
2. 检查 Token 是否有 `repo` 权限
3. 重新生成 Token

### 问题3：Render 部署失败

**可能原因**：
- requirements.txt 不完整
- Python 版本不兼容
- Procfile 配置错误

**解决方法**：
1. 检查 requirements.txt 是否包含所有依赖
2. 检查 Python 版本（Render 默认 Python 3.9+）
3. 查看部署日志

### 问题4：应用无法启动

**可能原因**：
- 启动命令错误
- 端口配置错误
- 依赖缺失

**解决方法**：
1. 检查 Start Command：`python backend/app.py`
2. 检查环境变量：`PORT=5006`
3. 查看应用日志

---

## 🎉 部署完成

您的应用现在已部署到 Render.com！

**访问地址**：`https://wukong-quant.onrender.com`

**登录凭证**：
- 用户名：`admin`
- 密码：`libo0519`

**重要提示**：
- ⚠️ 免费版会自动休眠（15 分钟无访问）
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
- Stack Overflow: 搜索 `render.com`

---

## 📝 详细文档

如果您需要更详细的说明，请查看：

- [RENDER_COMPLETE_GUIDE.md](d:\trae\备份悟空52224\RENDER_COMPLETE_GUIDE.md) - 完整部署指南
- [RENDER_QUICK_GUIDE.md](d:\trae\备份悟空52224\RENDER_QUICK_GUIDE.md) - 快速部署指南
- [FREE_CLOUD_SUMMARY.md](d:\trae\备份悟空52224\FREE_CLOUD_SUMMARY.md) - 免费云服务总结

---

**祝您部署顺利！** 🚀
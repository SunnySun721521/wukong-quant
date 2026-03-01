# 备份悟空52224 - PythonAnywhere 部署指南

## 📋 PythonAnywhere 简介

PythonAnywhere 是一个专门为 Python 应用设计的云服务平台，非常适合新手使用。

**优点**:
- ✅ 专门针对 Python 应用
- ✅ 配置简单，适合新手
- ✅ 提供在线编辑器
- ✅ 自动 HTTPS
- ✅ 免费版可用

**免费额度**:
- 1个 Web 应用
- 1个 Worker
- 512MB RAM
- 每天 3 小时运行时间

---

## 🚀 部署步骤

### 步骤1: 注册账号

1. 访问：https://www.pythonanywhere.com
2. 点击 "Create a beginner account"
3. 填写注册信息：
   - Username: 选择一个用户名
   - Email: 您的邮箱
   - Password: 设置密码
4. 点击 "Register"
5. 验证邮箱

### 步骤2: 创建 Web 应用

1. 登录 PythonAnywhere
2. 点击顶部菜单的 "Web" 标签
3. 点击 "Add a new web app" 按钮
4. 选择 "Flask"
5. 点击 "Next"
6. 配置应用信息：
   - Python version: 选择 "3.10" 或更高
   - Project name: 输入项目名称（如：wukong）
   - PythonAnywhere username: 自动填充
   - 点击 "Next"
7. 配置 WSGI：
   - WSGI configuration file: 自动生成
   - Virtualenv: 自动创建
   - 点击 "Next"
8. 等待应用创建完成

### 步骤3: 上传代码

**方式1: 使用在线编辑器（推荐新手）**

1. 点击顶部菜单的 "Files" 标签
2. 进入您的 home 目录
3. 点击 "New directory" 创建项目目录
4. 命名为 "wukong" 或您喜欢的名称
5. 进入新创建的目录
6. 点击 "Upload files" 上传文件
7. 选择以下文件上传：
   - `backend/app.py`
   - `backend/data/` (整个目录)
   - `web/` (整个目录)
   - `requirements.txt`
   - 其他必要文件

**方式2: 使用 Git（推荐）**

1. 在本地初始化 Git 仓库：
   ```bash
   cd d:\trae\备份悟空52224
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. 在 GitHub 创建仓库并推送

3. 在 PythonAnywhere 的 Bash 控制台：
   ```bash
   cd ~
   git clone https://github.com/yourusername/yourrepo.git wukong
   ```

**方式3: 使用 SCP（推荐）**

在本地 PowerShell 中：
```powershell
# 上传整个项目
scp -r "d:\trae\备份悟空52224\*" yourusername@ssh.pythonanywhere.com:~/wukong/
```

### 步骤4: 配置虚拟环境

1. 点击顶部菜单的 "Consoles" 标签
2. 点击 "Bash" 打开 Bash 控制台
3. 进入项目目录：
   ```bash
   cd ~/wukong
   ```

4. 激活虚拟环境：
   ```bash
   source ~/wukong-venv/bin/activate
   ```

5. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

6. 等待安装完成

### 步骤5: 配置 WSGI

1. 点击顶部菜单的 "Web" 标签
2. 找到您的 Web 应用
3. 点击应用名称
4. 找到 "Code" 部分
5. 点击 "WSGI configuration file" 链接
6. 编辑 WSGI 配置文件：

```python
import sys
import os

# 添加项目路径
project_home = '/home/yourusername/wukong'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 导入 Flask 应用
from backend.app import app as application

# 配置静态文件
application.static_folder = os.path.join(project_home, 'web')
```

7. 保存文件

### 步骤6: 配置 Web 应用

1. 返回 Web 应用页面
2. 找到 "Code" 部分
3. 修改以下设置：
   - Working directory: `/home/yourusername/wukong`
   - Virtualenv: `/home/yourusername/wukong-venv`
   - Python version: 选择 3.10 或更高
4. 点击 "Save"

### 步骤7: 配置静态文件

1. 在 Web 应用页面
2. 找到 "Static files" 部分
3. 点击 "Enter a URL to serve as a static file"
4. 添加静态文件映射：
   - URL: `/static/`
   - Directory: `/home/yourusername/wukong/web/static/`
5. 点击 "Save"

### 步骤8: 重载应用

1. 在 Web 应用页面
2. 点击 "Reload" 按钮
3. 等待应用重载完成

### 步骤9: 访问应用

1. 在 Web 应用页面
2. 找到 "Configuration" 部分
3. 复制显示的 URL
4. 在浏览器中打开
5. 访问登录页面：`https://yourusername.pythonanywhere.com/login.html`
6. 使用登录凭证：
   - 用户名: `admin`
   - 密码: `libo0519`

---

## 🔧 高级配置

### 配置自定义域名

1. 在 Web 应用页面
2. 找到 "Configuration" 部分
3. 点击 "Add a new domain"
4. 输入您的域名
5. 配置 DNS 记录：
   - 类型: CNAME
   - 名称: www
   - 值: yourusername.pythonanywhere.com
6. 等待 DNS 生效

### 配置 HTTPS

PythonAnywhere 自动提供 HTTPS，无需额外配置。

### 配置 Worker（定时任务）

1. 点击顶部菜单的 "Tasks" 标签
2. 点击 "Add a new task"
3. 配置任务：
   - Description: PDF Scheduler
   - Command: `cd ~/wukong && source ~/wukong-venv/bin/activate && python backend/pdf_scheduler.py`
   - Schedule: 选择定时
   - Hour: 17
   - Minute: 30
4. 点击 "Create"

---

## 📊 监控和日志

### 查看应用日志

1. 在 Web 应用页面
2. 找到 "Log files" 部分
3. 点击 "Error log" 或 "Server log"
4. 查看日志信息

### 查看应用状态

1. 在 Web 应用页面
2. 查看 "Running" 状态
3. 如果显示 "Stopped"，点击 "Reload"

---

## 🔧 故障排查

### 问题1: 应用无法启动

**解决方法**:
1. 检查 WSGI 配置是否正确
2. 检查依赖是否安装完整
3. 查看错误日志
4. 检查 Python 版本

### 问题2: 静态文件无法加载

**解决方法**:
1. 检查静态文件路径配置
2. 确保静态文件目录存在
3. 检查文件权限

### 问题3: 数据库连接失败

**解决方法**:
1. 检查数据库文件路径
2. 确保数据库文件有写入权限
3. 检查数据库配置

### 问题4: 超出免费额度

**解决方法**:
1. 查看使用情况
2. 升级到付费版
3. 或使用其他免费云服务

---

## 🎉 部署完成

您的应用现在已部署到 PythonAnywhere！

**访问地址**: `https://yourusername.pythonanywhere.com`

**登录凭证**:
- 用户名: `admin`
- 密码: `libo0519`

**重要提示**:
- ⚠️ 免费版每天运行 3 小时
- ⚠️ 应用会自动休眠
- ⚠️ 升级到付费版可无限运行

---

**祝您使用愉快！** 🚀
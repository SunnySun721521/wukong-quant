# 备份悟空52224 - 公网部署

## 📋 当前状态

- **本地应用**: ✅ 运行中 (端口 5006)
- **局域网访问**: http://172.168.1.58:5006
- **登录凭证**: admin / libo0519

---

## 🚀 快速开始

### 方式1: 使用一键部署脚本（推荐）

```powershell
# PowerShell
.\public_deployment.ps1
```

### 方式2: 直接运行隧道脚本

**serveo.net (推荐，无需注册)**:
```bash
python start_serveo.py
```

**localtunnel (推荐，无需注册)**:
```bash
python start_localtunnel.py
```

**pyngrok (最简单)**:
```bash
python start_public_tunnel.py
```

**Cloudflare Tunnel (长期稳定)**:
```bash
setup_cloudflare_tunnel.bat
start_cloudflare_tunnel.bat
```

---

## 📁 部署文件说明

| 文件 | 说明 |
|------|------|
| [public_deployment.ps1](d:\trae\备份悟空52224\public_deployment.ps1) | 一键部署脚本（PowerShell） |
| [start_serveo.py](d:\trae\备份悟空52224\start_serveo.py) | serveo.net 隧道脚本 |
| [start_localtunnel.py](d:\trae\备份悟空52224\start_localtunnel.py) | localtunnel 隧道脚本 |
| [start_public_tunnel.py](d:\trae\备份悟空52224\start_public_tunnel.py) | pyngrok 隧道脚本 |
| [setup_cloudflare_tunnel.bat](d:\trae\备份悟空52224\setup_cloudflare_tunnel.bat) | Cloudflare Tunnel 配置脚本 |
| [start_cloudflare_tunnel.bat](d:\trae\备份悟空52224\start_cloudflare_tunnel.bat) | Cloudflare Tunnel 启动脚本 |
| [PUBLIC_DEPLOYMENT_GUIDE.md](d:\trae\备份悟空52224\PUBLIC_DEPLOYMENT_GUIDE.md) | 详细部署指南 |

---

## 🎯 推荐方案

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 快速测试 | serveo.net | 无需注册，即开即用 |
| 演示展示 | localtunnel | 无需注册，功能完善 |
| 长期使用 | Cloudflare Tunnel | 免费且稳定，支持自定义域名 |
| Python 开发 | pyngrok | Python 原生支持 |

---

## 📝 使用步骤

1. **确保应用运行**
   ```bash
   cd backend
   python app.py
   ```

2. **选择方案并启动**
   ```bash
   # 运行一键脚本
   .\public_deployment.ps1
   
   # 或直接运行隧道脚本
   python start_serveo.py
   ```

3. **访问应用**
   - 复制脚本显示的公网地址
   - 在浏览器中打开
   - 访问登录页面: `/login.html`
   - 登录凭证: admin / libo0519

---

## 🔧 故障排查

### 问题1: 本地应用未运行

**解决方法**:
```bash
cd backend
python app.py
```

### 问题2: SSH 客户端未找到 (serveo.net)

**解决方法**:
- Windows: 启用 OpenSSH 客户端
  - 设置 > 应用 > 可选功能 > OpenSSH 客户端
- 下载 PuTTY: https://www.putty.org/

### 问题3: Node.js 未安装 (localtunnel)

**解决方法**:
- 访问: https://nodejs.org/
- 下载并安装 Node.js
- 验证安装: `node --version`

### 问题4: ngrok 需要注册

**解决方法**:
- 访问: https://dashboard.ngrok.com/signup
- 注册账号
- 获取 authtoken
- 配置: `ngrok config add-authtoken YOUR_TOKEN`

---

## 📊 方案对比

| 特性 | serveo.net | localtunnel | pyngrok | Cloudflare |
|------|-----------|-------------|---------|-----------|
| 价格 | 免费 | 免费 | 免费/付费 | 免费 |
| 注册 | 不需要 | 不需要 | 需要 | 需要 |
| 配置难度 | 低 | 低 | 低 | 中 |
| 自定义域名 | 不支持 | 不支持 | 付费支持 | 支持 |
| 自动 HTTPS | 支持 | 支持 | 支持 | 支持 |
| 稳定性 | 中 | 中 | 高 | 高 |
| 全球加速 | 不支持 | 不支持 | 不支持 | 支持 |

---

## 🎉 部署完成

选择任意一种方案启动后，您的应用将可以通过公网访问！

**重要提示**:
- ⚠️ 免费方案地址会变化
- ⚠️ 隧道窗口关闭后停止
- ⚠️ 生产环境建议使用云服务器

---

**祝您部署顺利！** 🚀
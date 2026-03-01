# Cloudflare Tunnel 公网部署方案

## 📋 方案概述

使用 **Cloudflare Tunnel** 实现免费、安全、稳定的公网部署。

**优点**：
- ✅ 完全免费
- ✅ 安全性高（Cloudflare CDN 保护）
- ✅ 支持自定义域名
- ✅ 全球加速
- ✅ 自动 HTTPS
- ✅ 无需公网 IP

---

## 🎯 部署步骤

### 步骤1：注册 Cloudflare 账号

1. 访问：https://dash.cloudflare.com/sign-up
2. 注册账号（免费）
3. 添加一个域名（如果没有域名，可以使用 Cloudflare 提供的临时域名）

### 步骤2：安装 Cloudflare Tunnel 工具

**Windows 安装**：
```bash
# 下载 cloudflared
# 访问：https://github.com/cloudflare/cloudflared/releases/latest
# 下载 Windows 版本：cloudflared-windows-amd64.exe

# 重命名为 cloudflared.exe
# 放到系统 PATH 或项目目录
```

**验证安装**：
```bash
cloudflared --version
```

### 步骤3：登录 Cloudflare

```bash
cloudflared tunnel login
```

这会打开浏览器，让你授权访问你的 Cloudflare 账号。

### 步骤4：创建 Tunnel

```bash
# 创建一个名为 backup-wukong 的 tunnel
cloudflared tunnel create backup-wukong
```

这会返回一个 Tunnel ID，记录下来。

### 步骤5：配置 Tunnel

创建配置文件 `cloudflared.yml`：

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: ./cloudflared-YOUR_TUNNEL_ID.json

ingress:
  - hostname: yourdomain.com  # 替换为你的域名
    service: http://localhost:5006
  - service: http_status:404
```

### 步骤6：运行 Tunnel

```bash
# 方式1：直接运行
cloudflared tunnel run backup-wukong

# 方式2：使用配置文件
cloudflared tunnel --config cloudflared.yml run

# 方式3：作为 Windows 服务运行
cloudflared service install
cloudflared service start
```

### 步骤7：访问应用

打开浏览器访问：`https://yourdomain.com`

---

## 🔧 Trae IDE + Cloudflare MCP Server

### 配置 Cloudflare MCP Server

1. 在 Trae IDE 中打开 MCP 设置
2. 添加 Cloudflare MCP Server
3. 配置 API Token

**获取 API Token**：
1. 访问：https://dash.cloudflare.com/profile/api-tokens
2. 创建 Token，权限选择：
   - Account - Cloudflare Tunnel - Edit
   - Zone - DNS - Edit

### 使用 AI 助手配置

在 Trae IDE 中，你可以通过对话方式让 AI 助手帮你配置：

**示例对话**：
```
你：帮我配置 Cloudflare Tunnel，将本地 5006 端口映射到公网

AI：好的，我来帮你配置。首先需要：
1. 创建 Tunnel
2. 配置 DNS 记录
3. 启动 Tunnel 服务

让我为你生成配置...
```

---

## 📝 完整配置示例

### cloudflared.yml
```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: ./cloudflared-a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  - hostname: wukong.yourdomain.com
    service: http://localhost:5006
  - service: http_status:404
```

### Windows 服务安装脚本 (install_tunnel_service.bat)
```batch
@echo off
echo 正在安装 Cloudflare Tunnel 服务...
cloudflared service install
echo 服务已安装
echo 正在启动服务...
cloudflared service start
echo 服务已启动
pause
```

---

## 🔒 安全配置

### 1. 启用 Cloudflare 访问控制

在 Cloudflare Dashboard 中：
1. 进入 Zero Trust > Access > Applications
2. 添加应用
3. 配置访问策略（例如：只允许特定邮箱访问）

### 2. 配置防火墙规则

在 Cloudflare Dashboard 中：
1. 进入 Security > WAF
2. 添加规则，例如：
   - 只允许特定国家/地区访问
   - 阻止恶意请求

### 3. 启用 Bot 保护

在 Cloudflare Dashboard 中：
1. 进入 Security > Bot Fight Mode
2. 启用 Bot 保护

---

## 📊 监控和日志

### 查看日志
```bash
cloudflared tunnel log backup-wukong
```

### Cloudflare Dashboard

1. 访问：https://dash.cloudflare.com
2. 进入 Zero Trust > Networks > Tunnels
3. 查看连接状态和流量统计

---

## 🎉 部署完成

配置完成后，你的应用将可以通过以下方式访问：

- **自定义域名**：https://wukong.yourdomain.com
- **自动 HTTPS**：Cloudflare 自动提供 SSL 证书
- **全球加速**：Cloudflare CDN 加速
- **安全保护**：Cloudflare WAF 保护

---

## 🆚 方案对比

| 特性 | Cloudflare Tunnel | ngrok | frp |
|------|-----------------|-------|-----|
| 价格 | 免费 | 免费/付费 | 免费 |
| 稳定性 | 高 | 中 | 高 |
| 配置难度 | 中 | 低 | 高 |
| 自定义域名 | 支持 | 付费支持 | 支持 |
| 自动 HTTPS | 支持 | 支持 | 需配置 |
| 全球加速 | 支持 | 不支持 | 不支持 |
| 安全保护 | 强 | 中 | 弱 |

---

## 📞 故障排查

### Tunnel 无法连接

1. 检查 cloudflared 是否运行
2. 检查本地应用是否运行（端口 5006）
3. 检查防火墙设置
4. 查看 Cloudflare Tunnel 日志

### 无法访问域名

1. 检查 DNS 记录是否正确
2. 检查域名是否指向 Cloudflare
3. 等待 DNS 传播（最多 24 小时）

---

## 🎯 推荐使用场景

**Cloudflare Tunnel 适合**：
- 长期使用
- 需要自定义域名
- 需要高安全性
- 需要全球加速

**ngrok 适合**：
- 临时测试
- 快速演示
- 不需要固定域名

---

**祝您部署顺利！** 🚀
# 备份悟空52224 公网部署方案

## 当前项目状态

### 应用信息
- **应用类型**: Flask Web应用
- **运行端口**: 5006
- **监听地址**: 0.0.0.0
- **本地IP**: 172.168.1.58
- **进程状态**: 运行中（PID: 21444）

### 项目结构
```
备份悟空52224/
├── backend/           # 后端Flask应用
│   ├── app.py        # 主应用文件
│   ├── data/         # 数据目录
│   ├── models/       # 模型文件
│   └── ...          # 其他文件
├── web/              # 前端文件
│   ├── login.html    # 登录页面
│   ├── index.html    # 首页
│   ├── plan.html     # 计划页面
│   └── ...          # 其他页面
└── ...              # 其他目录
```

## 公网部署方案

### 方案一：内网穿透（推荐用于测试）

#### 1. 使用ngrok（最简单）
```bash
# 下载ngrok: https://ngrok.com/download
# 注册账号获取authtoken

# 启动ngrok
ngrok http 5006
```

#### 2. 使用frp（稳定可靠）
需要一台有公网IP的服务器作为frp服务器。

**服务端配置（frps.ini）**:
```ini
[common]
bind_port = 7000
vhost_http_port = 8080
```

**客户端配置（frpc.ini）**:
```ini
[common]
server_addr = 你的服务器IP
server_port = 7000

[web]
type = http
local_ip = 127.0.0.1
local_port = 5006
custom_domains = yourdomain.com
```

### 方案二：云服务器部署（推荐用于生产）

#### 1. 准备工作
- 购买云服务器（阿里云、腾讯云、华为云等）
- 安装Python环境
- 上传项目文件

#### 2. 部署步骤
```bash
# 1. 安装依赖
pip install flask flask-cors requests pandas numpy

# 2. 配置防火墙
# 开放5006端口

# 3. 使用Gunicorn部署（生产环境推荐）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5006 app:app

# 4. 使用Nginx反向代理（可选但推荐）
```

**Nginx配置示例**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5006;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 方案三：Trae IDE部署（如果支持）

如果Trae IDE支持一键部署功能，可以使用内置的部署工具。

## 安全配置

### 1. 修改登录凭证
当前凭证：admin / libo0519
建议：修改为更强的密码

### 2. 配置HTTPS
使用Let's Encrypt免费SSL证书

### 3. 配置防火墙
只开放必要的端口（80, 443, 5006）

### 4. 启用访问日志
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('access.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

## 监控和维护

### 1. 进程监控
使用supervisor或systemd管理进程

**systemd配置示例**:
```ini
[Unit]
Description=Flask App
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/backup悟空52224/backend
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. 日志监控
定期检查应用日志和错误日志

### 3. 备份策略
定期备份数据库和重要文件

## 快速开始（内网穿透）

### 使用ngrok快速部署

1. **下载ngrok**
   - 访问 https://ngrok.com/download
   - 下载Windows版本
   - 解压到任意目录

2. **注册并获取authtoken**
   - 访问 https://dashboard.ngrok.com/signup
   - 注册账号
   - 获取authtoken

3. **配置ngrok**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

4. **启动ngrok**
   ```bash
   ngrok http 5006
   ```

5. **获取公网地址**
   ngrok会显示一个临时的公网地址，例如：
   ```
   Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:5006
   ```

6. **访问应用**
   - 使用ngrok提供的公网地址访问
   - 例如：https://xxxx-xx-xx-xx-xx.ngrok-free.app/login.html

## 注意事项

1. **免费ngrok地址会变化**，每次重启ngrok都会生成新的地址
2. **生产环境建议使用云服务器**，稳定性和安全性更好
3. **定期备份数据**，防止数据丢失
4. **监控服务器资源**，确保应用稳定运行
5. **及时更新依赖**，修复安全漏洞

## 当前应用访问地址

- **本地访问**: http://127.0.0.1:5006
- **局域网访问**: http://172.168.1.58:5006
- **公网访问**: 需要配置内网穿透或云服务器

## 下一步操作

1. 选择合适的部署方案
2. 准备相应的服务器或工具
3. 按照步骤进行部署
4. 测试公网访问
5. 配置安全措施
6. 设置监控和备份
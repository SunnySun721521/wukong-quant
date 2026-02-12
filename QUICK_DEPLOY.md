# 备份悟空52224 - 快速部署指南

## 📋 项目信息

- **项目名称**: 备份悟空52224（量化交易系统）
- **应用类型**: Flask Web应用
- **运行端口**: 5006
- **登录凭证**: admin / libo0519
- **当前状态**: 运行中（PID: 21444）

## 🚀 快速部署（3种方式）

### 方式1：ngrok（最简单，推荐测试）

**优点**: 最简单快速，无需服务器
**缺点**: 免费版地址会变化
**适合**: 测试、演示、临时使用

**步骤**:
1. 下载ngrok: https://ngrok.com/download
2. 注册账号: https://dashboard.ngrok.com/signup
3. 获取authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
4. 运行命令: `ngrok config add-authtoken YOUR_AUTHTOKEN`
5. 启动ngrok: `ngrok http 5006`
6. 复制显示的公网地址访问应用

**一键启动**:
```bash
# Windows
start_ngrok.bat

# Linux/Mac
ngrok http 5006
```

---

### 方式2：云服务器（推荐生产）

**优点**: 稳定可靠，固定域名，安全性高
**缺点**: 需要购买服务器
**适合**: 生产环境、长期使用

**步骤**:
1. 购买云服务器（阿里云、腾讯云、华为云等）
2. 安装Python环境
3. 上传项目文件
4. 安装依赖: `pip install -r requirements.txt`
5. 配置防火墙（开放5006端口）
6. 使用Gunicorn运行: `gunicorn -w 4 -b 0.0.0.0:5006 app:app`
7. 配置Nginx反向代理（可选但推荐）
8. 配置HTTPS（使用Let's Encrypt免费证书）

**详细配置**:
- 参考文件: `nginx.conf`
- 参考文件: `backup悟空52224.service`

---

### 方式3：内网穿透frp（稳定）

**优点**: 稳定可靠，可自定义域名
**缺点**: 需要一台有公网IP的服务器
**适合**: 有公网服务器的用户

**步骤**:
1. 准备一台有公网IP的服务器
2. 下载frp: https://github.com/fatedier/frp/releases
3. 配置服务端（frps.ini）
4. 配置客户端（frpc.ini）
5. 启动frpc客户端

---

## 📁 部署文件说明

| 文件 | 说明 |
|------|------|
| `DEPLOYMENT.md` | 详细部署文档 |
| `deploy.bat` | Windows部署脚本 |
| `start_ngrok.bat` | ngrok一键启动脚本 |
| `ngrok.yml` | ngrok配置文件 |
| `requirements.txt` | Python依赖列表 |
| `nginx.conf` | Nginx配置文件 |
| `backup悟空52224.service` | systemd服务配置 |

---

## 🔧 本地测试

### 启动应用
```bash
cd backend
python app.py
```

### 访问地址
- 本地: http://127.0.0.1:5006
- 局域网: http://172.168.1.58:5006

### 登录
- 用户名: `admin`
- 密码: `libo0519`

---

## 🔒 安全建议

1. **修改登录密码**: 当前密码过于简单
2. **启用HTTPS**: 使用Let's Encrypt免费SSL证书
3. **配置防火墙**: 只开放必要的端口
4. **定期备份**: 备份数据和配置文件
5. **监控日志**: 定期检查访问日志和错误日志
6. **更新依赖**: 及时更新Python包

---

## 📊 监控和维护

### 检查应用状态
```bash
# 检查端口
netstat -ano | findstr ":5006"

# 检查进程
tasklist | findstr python

# 查看日志
type backend\app.log
```

### 重启应用
```bash
# 停止应用
taskkill /F /PID 21444

# 启动应用
cd backend
python app.py
```

---

## 📞 技术支持

如有问题，请查看：
1. 详细部署文档: `DEPLOYMENT.md`
2. 应用日志: `backend/app.log`
3. 错误日志: `backend/error.log`

---

## ✅ 部署检查清单

- [ ] 应用正常运行
- [ ] 端口5006开放
- [ ] 登录功能正常
- [ ] 所有页面可访问
- [ ] API接口正常
- [ ] 数据库连接正常
- [ ] 定时任务运行正常
- [ ] 邮件发送正常
- [ ] 日志记录正常
- [ ] 备份策略配置

---

## 🎯 推荐方案

**测试/演示**: 使用ngrok（方式1）
**生产环境**: 使用云服务器（方式2）
**有公网服务器**: 使用frp（方式3）

---

**祝您部署顺利！** 🎉
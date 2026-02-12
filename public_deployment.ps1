# 备份悟空52224 - 公网部署启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "备份悟空52224 - 公网部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查应用是否运行
Write-Host "[检查] 本地应用状态..." -ForegroundColor Yellow
$portCheck = netstat -ano | Select-String ":5006" | Select-String "LISTENING"
if ($portCheck) {
    Write-Host "✓ 应用正在运行 (端口 5006)" -ForegroundColor Green
} else {
    Write-Host "✗ 应用未运行，正在启动..." -ForegroundColor Red
    Set-Location "$PSScriptRoot\backend"
    Start-Process -FilePath "python" -ArgumentList "app.py" -RedirectStandardOutput "app.log" -RedirectStandardError "error.log" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✓ 应用已启动" -ForegroundColor Green
    Set-Location $PSScriptRoot
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "选择公网部署方案" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. serveo.net (推荐)" -ForegroundColor White
Write-Host "   - 完全免费，无需注册" -ForegroundColor Gray
Write-Host "   - 需要安装 SSH 客户端" -ForegroundColor Gray
Write-Host ""
Write-Host "2. localtunnel (推荐)" -ForegroundColor White
Write-Host "   - 完全免费，无需注册" -ForegroundColor Gray
Write-Host "   - 需要安装 Node.js" -ForegroundColor Gray
Write-Host ""
Write-Host "3. pyngrok (最简单)" -ForegroundColor White
Write-Host "   - Python 原生支持" -ForegroundColor Gray
Write-Host "   - 需要注册 ngrok 账号" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Cloudflare Tunnel (长期稳定)" -ForegroundColor White
Write-Host "   - 免费且稳定，支持自定义域名" -ForegroundColor Gray
Write-Host "   - 配置相对复杂" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 查看详细部署文档" -ForegroundColor White
Write-Host ""
Write-Host "6. 退出" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请输入选项 (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "启动 serveo.net 隧道" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        python "$PSScriptRoot\start_serveo.py"
    }
    "2" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "启动 localtunnel 隧道" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        python "$PSScriptRoot\start_localtunnel.py"
    }
    "3" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "启动 pyngrok 隧道" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        python "$PSScriptRoot\start_public_tunnel.py"
    }
    "4" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Cloudflare Tunnel 部署" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请按照以下步骤操作：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 运行配置脚本: setup_cloudflare_tunnel.bat" -ForegroundColor White
        Write-Host "2. 启动隧道: start_cloudflare_tunnel.bat" -ForegroundColor White
        Write-Host ""
        Read-Host "按回车键继续"
    }
    "5" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "打开部署文档" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Start-Process "$PSScriptRoot\PUBLIC_DEPLOYMENT_GUIDE.md"
        Write-Host "已打开部署文档" -ForegroundColor Green
        Write-Host ""
        Read-Host "按回车键继续"
    }
    "6" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "感谢使用！" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        exit
    }
    default {
        Write-Host ""
        Write-Host "无效的选项，请重新运行脚本" -ForegroundColor Red
        Write-Host ""
        Read-Host "按回车键继续"
    }
}
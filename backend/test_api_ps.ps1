# 测试默认值
Write-Host "测试默认值:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5006/api/plan/position" -Method GET -UseBasicParsing
$content = $response.Content | ConvertFrom-Json
Write-Host "状态码: $($response.StatusCode)"
Write-Host "可用现金: $($content.available_cash)"
Write-Host "总资产: $($content.total_assets)"
Write-Host ""

# 测试自定义值
Write-Host "测试自定义值:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5006/api/plan/position?available_cash=200000" -Method GET -UseBasicParsing
$content = $response.Content | ConvertFrom-Json
Write-Host "状态码: $($response.StatusCode)"
Write-Host "可用现金: $($content.available_cash)"
Write-Host "总资产: $($content.total_assets)"
Write-Host ""

# 测试另一个自定义值
Write-Host "测试另一个自定义值:"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5006/api/plan/position?available_cash=300000" -Method GET -UseBasicParsing
$content = $response.Content | ConvertFrom-Json
Write-Host "状态码: $($response.StatusCode)"
Write-Host "可用现金: $($content.available_cash)"
Write-Host "总资产: $($content.total_assets)"
Write-Host ""

# 量化交易系统 - 微信小程序版

一个基于Python后端和微信小程序前端的量化交易回测与预测系统，专注于回测和预测功能，不需要实盘交易接口和邮件报警。

## 功能特性

- **股票池管理**：支持自定义股票代码，自动基于沪深300成分股进行动态调整
- **策略回测**：基于均线交叉策略进行历史数据回测，计算收益率、最大回撤、夏普比率等指标
- **AI预测**：使用机器学习模型（随机森林）预测股票未来走势
- **数据可视化**：精美的暗色主题界面，展示资金曲线、交易记录等
- **实时行情**：获取股票实时价格和涨跌幅信息

## 项目结构

```
悟空520/
├── backend/              # Python后端API服务
│   └── app.py          # Flask API服务
├── strategy/            # 策略模块
│   ├── data_provider.py      # 数据获取模块
│   ├── stock_pool_manager.py # 股票池管理
│   ├── backtest_engine.py    # 回测引擎
│   └── stock_predictor.py    # 预测模块
├── miniprogram/        # 微信小程序前端
│   ├── pages/          # 页面
│   │   ├── index/      # 首页
│   │   ├── backtest/   # 回测页面
│   │   ├── prediction/ # 预测页面
│   │   └── strategy/   # 策略页面
│   ├── utils/          # 工具类
│   └── app.js         # 小程序入口
├── logs/              # 日志文件目录
├── models/            # 模型文件目录
├── requirements.txt    # Python依赖
├── start_backend.bat  # 启动后端服务
└── install_dependencies.bat # 安装依赖
```

## 安装步骤

### 1. 安装Python依赖

双击运行 `install_dependencies.bat` 或在命令行中执行：

```bash
cd d:\trae\悟空520
pip install -r requirements.txt
```

### 2. 启动后端服务

双击运行 `start_backend.bat` 或在命令行中执行：

```bash
cd backend
python app.py
```

后端服务将在 `http://127.0.0.1:5001` 启动。

### 3. 配置微信小程序

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 在 `miniprogram/app.js` 中配置后端API地址：
   ```javascript
   globalData: {
     apiBaseUrl: 'http://127.0.0.1:5001',  // 修改为你的后端地址
   }
   ```

## 使用说明

### 首页

- 查看策略状态和股票池信息
- 查看关注股票的实时行情
- 快捷访问回测、预测等功能

### 策略回测

1. 输入股票代码（如600519）
2. 设置回测日期范围
3. 配置均线参数（快速均线、慢速均线）
4. 点击"开始回测"查看结果

### AI预测

1. 输入股票代码
2. 设置预测天数
3. 点击"开始预测"查看预测结果

### 股票池管理

1. 查看当前股票池中的股票
2. 添加或删除股票代码
3. 点击"更新股票池"自动基于沪深300成分股进行调整

## API接口

### 股票池管理

- `GET /api/stockpool/info` - 获取股票池信息
- `POST /api/stockpool/update` - 更新股票池（基于沪深300）
- `POST /api/stockpool/add` - 添加股票到池
- `POST /api/stockpool/remove` - 从池中删除股票

### 回测接口

- `GET /api/backtest/single` - 单股票回测
- `POST /api/backtest/multi` - 多股票回测

### 预测接口

- `GET /api/predict/single` - 单股票预测
- `POST /api/predict/batch` - 批量预测

### 数据接口

- `GET /api/stocks/attention` - 获取关注股票数据
- `GET /api/stocks/kline` - 获取K线数据
- `GET /api/hs300/components` - 获取沪深300成分股

### 策略接口

- `GET /api/strategy/status` - 获取策略状态
- `GET /api/strategy/params` - 获取策略参数

## 默认股票池

系统默认关注以下股票：
- 600519（贵州茅台）
- 002371（七星电子）
- 000858（五粮液）
- 002415（海康威视）
- 002236（大华股份）

## 注意事项

1. 本系统仅用于学习和研究，不构成投资建议
2. 股票数据来源于akshare，可能存在延迟
3. 预测结果仅供参考，不保证准确性
4. 请确保网络连接正常，以便获取实时数据

## 技术栈

- **后端**：Python + Flask + akshare + backtrader + scikit-learn
- **前端**：微信小程序原生开发
- **数据**：akshare（中国股票数据接口）
- **回测**：backtrader
- **预测**：scikit-learn（随机森林回归）

## 许可证

MIT License
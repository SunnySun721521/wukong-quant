const app = getApp();
const request = require('../../utils/request');

Page({
  data: {
    symbol: '600519',
    stockPool: [],
    showStockPicker: false,
    startDate: '2010-01-01',
    endDate: '',
    today: '',
    fastPeriod: 5,
    slowPeriod: 20,
    loading: false,
    result: null,
    error: null
  },

  onLoad() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayStr = `${year}-${month}-${day}`;
    
    const startDate = '2020-01-01';
    this.setData({
      endDate: todayStr,
      today: todayStr
    });
    this.loadStockPool();
  },

  onShow() {
    const lastUpdateTime = app.globalData.stockPoolUpdateTime || 0;
    const currentTime = new Date().getTime();
    const timeDiff = currentTime - lastUpdateTime;
    
    console.log('Backtest page stock pool update time diff:', timeDiff);
    
    if (timeDiff < 1000) {
      console.log('Stock pool was just updated, reloading data');
      this.loadStockPool();
    }
  },

  loadStockPool() {
    request.get('/api/stockpool/info', {}, { showLoading: false })
      .then(res => {
        if (res && res.current_pool) {
          this.setData({
            stockPool: res.current_pool
          });
        }
      })
      .catch(err => {
        console.error('Failed to load stock pool:', err);
      });
  },

  onSymbolInput(e) {
    this.setData({ symbol: e.detail.value });
  },

  onStockPickerToggle() {
    this.setData({
      showStockPicker: !this.data.showStockPicker
    });
  },

  onStockSelect(e) {
    const symbol = e.currentTarget.dataset.symbol;
    this.setData({
      symbol: symbol,
      showStockPicker: false
    });
  },

  onStartDateChange(e) {
    this.setData({ startDate: e.detail.value });
  },

  onEndDateChange(e) {
    this.setData({ endDate: e.detail.value });
  },

  onFastPeriodInput(e) {
    this.setData({ fastPeriod: e.detail.value });
  },

  onSlowPeriodInput(e) {
    this.setData({ slowPeriod: e.detail.value });
  },

  runBacktest() {
    if (!this.data.symbol) {
      wx.showToast({
        title: '请输入股票代码',
        icon: 'none'
      });
      return;
    }

    if (!this.data.fastPeriod || !this.data.slowPeriod) {
      wx.showToast({
        title: '请输入均线参数',
        icon: 'none'
      });
      return;
    }

    this.setData({ loading: true, result: null, error: null });

    const startDate = this.data.startDate.replace(/-/g, '');
    const endDate = this.data.endDate.replace(/-/g, '');

    request.get('/api/backtest/single', {
      symbol: this.data.symbol,
      start_date: startDate,
      end_date: endDate,
      fast_period: parseInt(this.data.fastPeriod),
      slow_period: parseInt(this.data.slowPeriod)
    })
      .then(res => {
        this.setData({ loading: false, result: res.result });
        this.drawEquityChart(res.result.equity_curve);
      })
      .catch(err => {
        this.setData({ loading: false, error: err.message || '回测失败' });
      });
  },

  drawEquityChart(equityCurve) {
    const query = wx.createSelectorQuery();
    query.select('#equityChart')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res || !res[0] || !res[0].node) {
          console.error('Canvas node not found');
          return;
        }

        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        
        const dpr = wx.getSystemInfoSync().pixelRatio;
        const width = res[0].width;
        const height = res[0].height;
        
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        
        const padding = 40;
        ctx.clearRect(0, 0, width, height);
        
        if (!equityCurve || equityCurve.length === 0) {
          return;
        }

        const values = equityCurve.map(item => item.value);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const valueRange = maxValue - minValue || 1;

        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        ctx.beginPath();
        ctx.strokeStyle = '#1890ff';
        ctx.lineWidth = 2;

        equityCurve.forEach((item, index) => {
          const x = padding + (index / (equityCurve.length - 1)) * chartWidth;
          const y = padding + chartHeight - ((item.value - minValue) / valueRange) * chartHeight;

          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });

        ctx.stroke();

        ctx.fillStyle = 'rgba(24, 144, 255, 0.1)';
        ctx.beginPath();
        ctx.moveTo(padding, padding + chartHeight);
        equityCurve.forEach((item, index) => {
          const x = padding + (index / (equityCurve.length - 1)) * chartWidth;
          const y = padding + chartHeight - ((item.value - minValue) / valueRange) * chartHeight;
          ctx.lineTo(x, y);
        });
        ctx.lineTo(padding + chartWidth, padding + chartHeight);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = '#ffffff';
        ctx.font = '20rpx sans-serif';
        ctx.fillText(minValue.toFixed(0), 0, padding + chartHeight);
        ctx.fillText(maxValue.toFixed(0), 0, padding);
      });
  },

  onPullDownRefresh() {
    if (this.data.result) {
      this.runBacktest();
    }
    wx.stopPullDownRefresh();
  }
});
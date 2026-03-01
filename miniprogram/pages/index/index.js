const app = getApp();
const request = require('../../utils/request');

Page({
  data: {
    stocks: [],
    loading: true,
    strategyStatus: {
      isRunning: false
    },
    stockPoolSize: 0,
    hs300Size: 0,
    portfolioResult: null,
    stockPool: [],
    stockRealtimeData: {},
    stockNames: {
      '600519': '贵州茅台',
      '000858': '五粮液',
      '002371': '北方华创',
      '002415': '海康威视',
      '002236': '大华股份'
    }
  },

  onLoad: function (options) {
    console.log('index page onLoad');
    this.loadStockPoolInfo();
  },

  onShow: function () {
    console.log('index page onShow');
    this.loadStockPoolInfo();
  },

  loadStockPoolInfo: function () {
    request.get('/api/stockpool/info', {}, { showLoading: false })
      .then(res => {
        console.log('Stock pool info:', res);
        if (res) {
          this.setData({
            stockPoolSize: res.pool_size || 0,
            hs300Size: res.hs300_size || 0,
            stockPool: res.current_pool || [],
            loading: false
          });
          
          if (res.current_pool && res.current_pool.length > 0) {
            this.loadRealtimeStockData();
            this.loadPortfolioData();
          }
        }
      })
      .catch(err => {
        console.error('Failed to load stock pool info:', err);
        this.setData({
          loading: false
        });
      });
  },

  loadRealtimeStockData: function () {
    if (this.data.stockPool.length === 0) {
      return;
    }

    request.get('/api/stocks/attention', { stocks: this.data.stockPool.join(',') }, { showLoading: false })
      .then(res => {
        console.log('Realtime stock data response:', res);
        console.log('Stocks array:', res.stocks);
        
        if (res && res.stocks && res.stocks.length > 0) {
          const realtimeData = {};
          res.stocks.forEach(stock => {
            console.log('Processing stock:', stock.symbol, stock);
            realtimeData[stock.symbol] = stock;
          });
          console.log('Final realtimeData:', realtimeData);
          this.setData({
            stockRealtimeData: realtimeData
          });
        } else {
          console.warn('No stock data received or empty array');
        }
      })
      .catch(err => {
        console.error('Failed to load realtime stock data:', err);
      });
  },

  loadPortfolioData: function () {
    console.log('Loading portfolio data...');
    
    if (this.data.stockPool.length === 0) {
      console.log('Stock pool is empty, skipping portfolio data loading');
      return;
    }

    const today = new Date();
    const endDate = today.toISOString().split('T')[0];
    const startDate = '20240101';

    request.post('/api/backtest/multi', {
      symbols: this.data.stockPool,
      start_date: startDate,
      end_date: endDate.replace(/-/g, ''),
      fast_period: 5,
      slow_period: 20
    }, { showLoading: false })
      .then(res => {
        console.log('Portfolio data loaded:', res);
        if (res && res.result) {
          this.setData({
            portfolioResult: res.result
          });
        }
      })
      .catch(err => {
        console.error('Failed to load portfolio data:', err);
      });
  },

  refreshStocks: function () {
    this.loadStockPoolInfo();
    
    wx.showToast({
      title: '刷新成功',
      icon: 'success',
      duration: 1000
    });
  },

  updateStockPool: function () {
    wx.showLoading({
      title: '更新中...'
    });

    request.post('/api/stockpool/update', {})
      .then(res => {
        wx.hideLoading();
        wx.showToast({
          title: '股票池更新成功',
          icon: 'success'
        });
        this.loadStockPoolInfo();
      })
      .catch(err => {
        wx.hideLoading();
        wx.showToast({
          title: '更新失败',
          icon: 'none'
        });
      });
  },

  formatVolume: function (volume) {
    if (volume >= 100000000) {
      return (volume / 100000000).toFixed(2) + '亿';
    } else if (volume >= 10000) {
      return (volume / 10000).toFixed(2) + '万';
    } else {
      return volume.toString();
    }
  },

  navigateToBacktest: function () {
    wx.switchTab({
      url: '/pages/backtest/backtest'
    });
  },

  navigateToPrediction: function () {
    wx.switchTab({
      url: '/pages/prediction/prediction'
    });
  },

  navigateToStrategy: function () {
    wx.switchTab({
      url: '/pages/strategy/strategy'
    });
  },

  navigateToSettings: function () {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  onHide: function () {
  },

  onUnload: function () {
  },

  onPullDownRefresh: function () {
    this.loadStockPoolInfo();
    wx.stopPullDownRefresh();
  },

  onReachBottom: function () {
  },

  onShareAppMessage: function () {
    return {
      title: '量化交易系统',
      path: '/pages/index/index'
    };
  }
})
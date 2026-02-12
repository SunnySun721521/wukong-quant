const app = getApp();
const request = require('../../utils/request');

Page({
  data: {
    strategyStatus: {
      isRunning: false,
      stock_pool_size: 0,
      hs300_size: 0
    },
    strategyParams: {
      peThreshold: 30,
      roeThreshold: 10,
      smaShort: 5,
      smaLong: 20,
      position_pct: 20.0
    },
    stockPoolInfo: {
      current_pool: [],
      pool_size: 0,
      hs300_size: 0
    },
    backtest: null,
    loading: true,
    updatingPool: false,
    newStockCode: '',
    activeTab: 'status'
  },

  onLoad(options) {
    this.loadStrategyData();
  },

  onShow() {
    this.loadStrategyData();
  },

  loadStrategyData() {
    this.setData({
      loading: true
    });

    Promise.all([
      this.loadStrategyStatus(),
      this.loadStrategyParams(),
      this.loadStockPoolInfo(),
      this.loadBacktest()
    ]).then(() => {
      this.setData({
        loading: false
      });
    }).catch(err => {
      console.error('Failed to load strategy data:', err);
      this.setData({
        loading: false
      });
    });
  },

  loadStrategyStatus() {
    return new Promise((resolve, reject) => {
      request.get('/api/strategy/status', {}, { showLoading: false })
        .then(res => {
          if (res) {
            const strategyStatus = {
              isRunning: res.status === 'running',
              stock_pool_size: res.stock_pool_size || 0,
              hs300_size: res.hs300_size || 0
            };
            
            this.setData({
              strategyStatus
            });
            
            app.globalData.strategyStatus = strategyStatus;
          }
          resolve();
        })
        .catch(err => {
          console.error('Failed to load strategy status:', err);
          reject(err);
        });
    });
  },

  loadStrategyParams() {
    return new Promise((resolve, reject) => {
      request.get('/api/strategy/params', {}, { showLoading: false })
        .then(res => {
          if (res) {
            this.setData({
              strategyParams: res
            });
          }
          resolve();
        })
        .catch(err => {
          console.error('Failed to load strategy params:', err);
          reject(err);
        });
    });
  },

  loadStockPoolInfo() {
    return new Promise((resolve, reject) => {
      request.get('/api/stockpool/info', {}, { showLoading: false })
        .then(res => {
          if (res) {
            this.setData({
              stockPoolInfo: res
            });
          }
          resolve();
        })
        .catch(err => {
          console.error('Failed to load stock pool info:', err);
          reject(err);
        });
    });
  },

  loadBacktest() {
    return new Promise((resolve, reject) => {
      request.get('/api/backtest/single', {
        symbol: '600519',
        start_date: '20230101',
        end_date: new Date().toISOString().slice(0, 10).replace(/-/g, '')
      }, { showLoading: false })
        .then(res => {
          if (res && res.result) {
            this.setData({
              backtest: res.result
            });
          }
          resolve();
        })
        .catch(err => {
          console.error('Failed to load backtest results:', err);
          resolve();
        });
    });
  },

  onTabClick(e) {
    this.setData({
      activeTab: e.currentTarget.dataset.tab
    });
  },

  refreshStockPool() {
    this.loadStockPoolInfo();
    wx.showToast({
      title: '刷新成功',
      icon: 'success'
    });
  },

  onStockCodeInput(e) {
    this.setData({
      newStockCode: e.detail.value
    });
  },

  addToPool() {
    if (!this.data.newStockCode) {
      wx.showToast({
        title: '请输入股票代码',
        icon: 'none'
      });
      return;
    }

    request.post('/api/stockpool/add', {
      stock_code: this.data.newStockCode
    })
      .then(res => {
        wx.showToast({
          title: res.message || '添加成功',
          icon: 'success'
        });
        this.setData({
          newStockCode: ''
        });
        this.loadStockPoolInfo();
        
        app.globalData.stockPoolUpdated = true;
        app.globalData.stockPoolUpdateTime = new Date().getTime();
      })
      .catch(err => {
        wx.showToast({
          title: err.message || '添加失败',
          icon: 'none'
        });
      });
  },

  removeFromPool(e) {
    const symbol = e.currentTarget.dataset.symbol;
    
    wx.showModal({
      title: '确认删除',
      content: `确定要从股票池中删除 ${symbol} 吗？`,
      success: (res) => {
        if (res.confirm) {
          request.post('/api/stockpool/remove', {
            stock_code: symbol
          })
            .then(res => {
              wx.showToast({
                title: res.message || '删除成功',
                icon: 'success'
              });
              this.loadStockPoolInfo();
              
              app.globalData.stockPoolUpdated = true;
              app.globalData.stockPoolUpdateTime = new Date().getTime();
            })
            .catch(err => {
              wx.showToast({
                title: err.message || '删除失败',
                icon: 'none'
              });
            });
        }
      }
    });
  },

  updateStockPool() {
    this.setData({
      updatingPool: true
    });

    request.post('/api/stockpool/update', {})
      .then(res => {
        this.setData({
          updatingPool: false
        });
        wx.showToast({
          title: res.message || '更新成功',
          icon: 'success'
        });
        this.loadStockPoolInfo();
        
        app.globalData.stockPoolUpdated = true;
        app.globalData.stockPoolUpdateTime = new Date().getTime();
      })
      .catch(err => {
        this.setData({
          updatingPool: false
        });
        wx.showToast({
          title: err.message || '更新失败',
          icon: 'none'
        });
      });
  },

  onHide() {
  },

  onUnload() {
  },

  onPullDownRefresh() {
    this.loadStrategyData();
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
  },

  onShareAppMessage() {
    return {
      title: '策略分析',
      path: '/pages/strategy/strategy'
    };
  }
})
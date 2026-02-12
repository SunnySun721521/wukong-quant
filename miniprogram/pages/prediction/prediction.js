const app = getApp();
const request = require('../../utils/request');

Page({
  data: {
    stockList: [],
    stockPool: [],
    startDate: '20240101',
    endDate: '',
    today: '',
    fastPeriod: 5,
    slowPeriod: 20,
    loading: false,
    results: [],
    portfolioResult: null,
    error: null
  },

  onLoad() {
    const today = new Date();
    const endDate = today.toISOString().split('T')[0];
    this.setData({
      endDate: endDate,
      today: endDate
    });
    this.loadStockPool();
  },

  onShow() {
    console.log('Prediction page onShow');
    this.loadStockPool();
  },

  loadStockPool() {
    request.get('/api/stockpool/info', {}, { showLoading: false })
      .then(res => {
        if (res && res.current_pool) {
          this.setData({
            stockPool: res.current_pool,
            stockList: res.current_pool
          });
          
          if (res.current_pool.length > 0) {
            this.runStrategyAnalysis();
          }
        }
      })
      .catch(err => {
        console.error('Failed to load stock pool:', err);
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

  runStrategyAnalysis() {
    if (this.data.stockList.length === 0) {
      console.log('Stock list is empty, skipping strategy analysis');
      return;
    }

    this.setData({ loading: true, results: [], portfolioResult: null, error: null });

    const startDate = this.data.startDate.replace(/-/g, '');
    const endDate = this.data.endDate.replace(/-/g, '');

    request.post('/api/backtest/multi', {
      symbols: this.data.stockList,
      start_date: startDate,
      end_date: endDate,
      fast_period: parseInt(this.data.fastPeriod),
      slow_period: parseInt(this.data.slowPeriod)
    })
      .then(res => {
        this.setData({ 
          loading: false, 
          results: res.result.individual_results || [],
          portfolioResult: res.result
        });
      })
      .catch(err => {
        this.setData({ loading: false, error: err.message || '策略分析失败' });
      });
  },

  getPerformanceColor(value) {
    if (value > 0) return '#52c41a';
    if (value < 0) return '#ff4d4f';
    return '#999999';
  },

  getPerformanceText(value) {
    if (value > 0) return '+' + value.toFixed(2) + '%';
    return value.toFixed(2) + '%';
  },

  onPullDownRefresh() {
    this.loadStockPool();
    wx.stopPullDownRefresh();
  }
})
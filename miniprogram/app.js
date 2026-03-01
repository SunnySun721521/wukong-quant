const request = require('./utils/request');

App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://127.0.0.1:5001',
    strategyStatus: {
      isRunning: false
    },
    stockPoolUpdated: false,
    stockPoolUpdateTime: 0
  },

  onLaunch() {
    console.log('小程序启动');
    
    wx.getWindowInfo({
      success: res => {
        this.globalData.windowInfo = res;
      }
    });
    
    setTimeout(() => {
      this.updateStrategyStatus();
    }, 1000);
  },

  onShow() {
    console.log('小程序显示');
  },

  onHide() {
    console.log('小程序隐藏');
  },

  updateStrategyStatus() {
    request.get('/api/strategy/status', {}, { showLoading: false })
      .then(res => {
        if (res) {
          this.globalData.strategyStatus = {
            isRunning: res.status === 'running'
          };
        }
      })
      .catch(err => {
        console.error('更新策略状态失败:', err);
      });
  }
})
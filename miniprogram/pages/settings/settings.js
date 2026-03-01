Page({
  data: {
    serverUrl: 'http://127.0.0.1:5001',
    testResult: null,
    testing: false
  },

  onLoad() {
    const app = getApp();
    if (app.globalData && app.globalData.apiBaseUrl) {
      this.setData({
        serverUrl: app.globalData.apiBaseUrl
      });
    }
  },

  onServerUrlInput(e) {
    this.setData({
      serverUrl: e.detail.value
    });
  },

  testConnection() {
    if (!this.data.serverUrl) {
      wx.showToast({
        title: '请输入服务器地址',
        icon: 'none'
      });
      return;
    }

    this.setData({
      testing: true,
      testResult: null
    });

    wx.request({
      url: `${this.data.serverUrl}/health`,
      method: 'GET',
      success: (res) => {
        this.setData({
          testing: false,
          testResult: {
            success: res.statusCode === 200,
            message: res.statusCode === 200 ? '连接成功' : '连接失败'
          }
        });

        if (res.statusCode === 200) {
          const app = getApp();
          app.globalData.apiBaseUrl = this.data.serverUrl;
          
          wx.showToast({
            title: '服务器地址已保存',
            icon: 'success'
          });

          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        }
      },
      fail: (err) => {
        this.setData({
          testing: false,
          testResult: {
            success: false,
            message: '连接失败：' + (err.errMsg || '未知错误')
          }
        });
      }
    });
  },

  saveServerUrl() {
    if (!this.data.serverUrl) {
      wx.showToast({
        title: '请输入服务器地址',
        icon: 'none'
      });
      return;
    }

    const app = getApp();
    app.globalData.apiBaseUrl = this.data.serverUrl;

    wx.showToast({
      title: '服务器地址已保存',
      icon: 'success'
    });

    setTimeout(() => {
      wx.navigateBack();
    }, 1000);
  }
})
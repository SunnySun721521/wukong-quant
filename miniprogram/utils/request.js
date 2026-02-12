const DEFAULT_TIMEOUT = 30000;
const DEFAULT_API_BASE_URL = 'http://172.168.1.58:5001';

function request(options) {
  const {
    url,
    method = 'GET',
    data = {},
    header = {},
    timeout = DEFAULT_TIMEOUT,
    showLoading = true,
    loadingText = '加载中...'
  } = options;

  if (showLoading) {
    wx.showLoading({
      title: loadingText,
      mask: true
    });
  }

  const app = getApp();
  
  let requestUrl;
  
  if (url.startsWith('http')) {
    requestUrl = url;
  } else {
    const apiBaseUrl = app && app.globalData && app.globalData.apiBaseUrl ? app.globalData.apiBaseUrl : DEFAULT_API_BASE_URL;
    requestUrl = `${apiBaseUrl}${url}`;
  }

  console.log('Request URL:', requestUrl);

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      if (showLoading) {
        wx.hideLoading();
      }
      wx.showToast({
        title: '请求超时',
        icon: 'none'
      });
      reject(new Error('Request timeout'));
    }, timeout);

    wx.request({
      url: requestUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res) => {
        clearTimeout(timer);

        if (showLoading) {
          wx.hideLoading();
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          wx.showToast({
            title: `请求失败(${res.statusCode})`,
            icon: 'none'
          });
          reject(new Error(`HTTP error ${res.statusCode}`));
        }
      },
      fail: (err) => {
        clearTimeout(timer);

        if (showLoading) {
          wx.hideLoading();
        }

        console.error('Request failed:', err);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

request.get = (url, data, options = {}) => {
  return request({
    url,
    method: 'GET',
    data,
    ...options
  });
};

request.post = (url, data, options = {}) => {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  });
};

request.put = (url, data, options = {}) => {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  });
};

request.delete = (url, data, options = {}) => {
  return request({
    url,
    method: 'DELETE',
    data,
    ...options
  });
};

module.exports = request;
# Render 构建脚本
# 安装中文字体支持

echo "Installing Chinese fonts for Render..."

# 更新包列表
apt-get update

# 安装中文字体
apt-get install -y fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei

# 刷新字体缓存
fc-cache -f -v

echo "Chinese fonts installed successfully!"

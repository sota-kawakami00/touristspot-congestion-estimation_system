#!/bin/bash

# Raspberry Pi Sensor Monitoring System セットアップスクリプト
# このスクリプトは必要なライブラリとシステム設定を行います

echo "=========================================="
echo "Raspberry Pi センサーモニタリングシステム"
echo "セットアップスクリプト"
echo "=========================================="

# エラー時に停止
set -e

# 実行権限チェック
if [ "$EUID" -ne 0 ]; then
    echo "このスクリプトはroot権限で実行してください"
    echo "sudo ./install_setup.sh"
    exit 1
fi

echo "システムパッケージを更新中..."
apt update && apt upgrade -y

echo "必要なシステムパッケージをインストール中..."
apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    build-essential \
    git \
    cmake \
    pkg-config \
    libglib2.0-dev \
    libpcsclite-dev \
    pcscd \
    pcsc-tools \
    libnfc-dev \
    libnfc-bin

echo "Pythonライブラリをインストール中..."

# システムパッケージとしてインストール
apt install -y \
    python3-rpi.gpio \
    python3-tk

# pipでインストール（--break-system-packagesフラグを使用）
pip3 install --upgrade pip --break-system-packages

# requirements.txtからインストール
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --break-system-packages
    # Adafruit-DHTは--force-piオプションで強制インストール
    pip3 install Adafruit-DHT --global-option="build_ext" --global-option="--force-pi" --break-system-packages
else
    echo "requirements.txtが見つかりません。手動でライブラリをインストールします..."
    pip3 install RPi.GPIO nfcpy --break-system-packages
    # Adafruit-DHTは--force-piオプションで強制インストール
    pip3 install Adafruit-DHT --global-option="build_ext" --global-option="--force-pi" --break-system-packages
fi

echo "GPIO権限設定..."
usermod -a -G gpio pi
usermod -a -G spi pi
usermod -a -G i2c pi

echo "NFC/PC/SC設定..."
systemctl enable pcscd
systemctl start pcscd

# ログディレクトリ作成
echo "ログディレクトリを作成中..."
mkdir -p /var/log
touch /var/log/sensor_system.log
touch /var/log/sensor_data.json
chown pi:pi /var/log/sensor_system.log
chown pi:pi /var/log/sensor_data.json

# systemdサービスファイル作成
echo "システムサービスを設定中..."
cat > /etc/systemd/system/sensor-monitoring.service << 'EOF'
[Unit]
Description=Sensor Monitoring System
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/sensor-monitoring
ExecStart=/usr/bin/python3 /home/pi/sensor-monitoring/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 設定ファイルのコピー（必要に応じて）
echo "設定ファイルを準備中..."
if [ ! -d "/home/pi/sensor-monitoring" ]; then
    mkdir -p /home/pi/sensor-monitoring
    chown pi:pi /home/pi/sensor-monitoring
fi

# GPU分割設定（GUI用）
echo "GPU設定を確認中..."
if ! grep -q "gpu_mem=128" /boot/config.txt; then
    echo "gpu_mem=128" >> /boot/config.txt
    echo "GPU設定を追加しました。再起動後に有効になります。"
fi

# I2C/SPI有効化
echo "I2C/SPIを有効化中..."
raspi-config nonint do_i2c 0
raspi-config nonint do_spi 0

# システムサービス有効化
systemctl daemon-reload
systemctl enable sensor-monitoring.service

echo "=========================================="
echo "セットアップ完了！"
echo "=========================================="
echo ""
echo "次の手順を実行してください："
echo "1. システムを再起動してください："
echo "   sudo reboot"
echo ""
echo "2. 再起動後、以下のコマンドでシステムを起動できます："
echo "   sudo systemctl start sensor-monitoring"
echo ""
echo "3. システム状態を確認："
echo "   sudo systemctl status sensor-monitoring"
echo ""
echo "4. ログを確認："
echo "   sudo journalctl -u sensor-monitoring -f"
echo ""
echo "5. 手動でテスト実行："
echo "   cd /home/pi/sensor-monitoring && python3 main.py"
echo ""
echo "注意："
echo "- NFCリーダーが正しく接続されていることを確認してください"
echo "- センサーのピン配置が config.py と一致していることを確認してください"
echo "- 必要に応じて config.py でピン番号を調整してください"
echo ""
echo "トラブルシューティング："
echo "- NFCテスト: nfc-list"
echo "- GPIO確認: gpio readall"
echo "- I2C確認: i2cdetect -y 1"
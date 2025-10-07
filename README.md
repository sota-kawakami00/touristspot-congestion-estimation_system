# Raspberry Pi センサーモニタリングシステム

ラズベリーパイを使用したセンサーデータ監視システムです。NFCカード認証によるセキュアなアクセス制御機能付き。

## 🔧 ハードウェア構成

### 必要な機器

1. **Raspberry Pi 4 Model B 8GB** (メインコンピュータ)
2. **PIRモーションセンサー** - 人感センサー（検出角度115°、最大8m）
3. **HC-SR04超音波距離センサー** - 距離測定（0.02m-4.5m）
4. **AM2302温湿度センサー** - 温度・湿度測定
5. **SONY NFCリーダー** - カード認証用
6. **Heltec LoRa32 V3** - 通信モジュール（オプション）

### 配線図

```
Raspberry Pi GPIO配置:

PIRモーションセンサー:
- VCC → 5V (Pin 2)
- GND → GND (Pin 6)
- OUT → GPIO 18 (Pin 12)

HC-SR04距離センサー:
- VCC → 5V (Pin 4)
- GND → GND (Pin 14)
- Trig → GPIO 23 (Pin 16)
- Echo → GPIO 24 (Pin 18)

AM2302温湿度センサー:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 9)
- DATA → GPIO 4 (Pin 7)

SONY NFCリーダー:
- USB接続
```

## 🚀 セットアップ

### 1. システムインストール

```bash
# リポジトリをクローン
git clone [repository-url]
cd touristspot-congestion-estimation_system

# セットアップスクリプト実行（要root権限）
sudo ./install_setup.sh

# システム再起動
sudo reboot
```

### 2. 設定ファイル調整

必要に応じて `config.py` でピン配置や設定を調整：

```python
# GPIO ピン設定
MOTION_SENSOR_PIN = 18
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24
TEMP_HUMIDITY_PIN = 4
```

### 3. 認証カード設定

`auth/nfc_reader.py` または `config.py` で認証済みカードIDを設定：

```python
AUTHORIZED_CARDS = [
    "01020304",  # あなたのカードID
    "ABCDEF01",  # 管理者カード
]
```

## 🎯 使用方法

### 手動起動

```bash
cd /home/pi/sensor-monitoring
python3 main.py
```

### サービスとして起動

```bash
# サービス開始
sudo systemctl start sensor-monitoring

# サービス停止
sudo systemctl stop sensor-monitoring

# 自動起動有効化
sudo systemctl enable sensor-monitoring

# ログ確認
sudo journalctl -u sensor-monitoring -f
```

### 操作手順

1. **システム起動**
   - プログラムを実行すると認証待機状態になります

2. **NFC認証**
   - SONY NFCリーダーに登録済みカードをタッチ
   - 認証成功でシステムが開始されます

3. **モニタリング**
   - リアルタイムでセンサーデータが表示されます
   - GUI画面でデータを確認できます

## 📊 機能

### センサー監視
- **人感センサー**: 人の動きを検出（115°範囲、最大8m）
- **距離センサー**: 超音波による距離測定（2cm-450cm）
- **温湿度センサー**: 環境温度・湿度監視

### セキュリティ
- **NFC認証**: カードタッチによるアクセス制御
- **カードID暗号化**: SHA256ハッシュ化による安全な認証

### 表示機能
- **リアルタイム表示**: 1秒間隔でのデータ更新
- **GUI インターフェース**: 直感的な操作画面
- **データログ**: 最新10件のデータ履歴表示

## 📁 ファイル構成

```
touristspot-congestion-estimation_system/
├── main.py                     # メインプログラム
├── config.py                   # システム設定
├── requirements.txt            # 依存ライブラリ
├── install_setup.sh           # セットアップスクリプト
├── README.md                  # このファイル
├── sensors/                   # センサーモジュール
│   ├── __init__.py
│   ├── motion_sensor.py       # PIRセンサー制御
│   ├── distance_sensor.py     # 距離センサー制御
│   └── temperature_humidity_sensor.py  # 温湿度センサー制御
├── auth/                      # 認証モジュール
│   ├── __init__.py
│   └── nfc_reader.py          # NFC認証制御
└── display/                   # 表示モジュール
    ├── __init__.py
    └── gui_display.py         # GUI表示制御
```

## 🔧 トラブルシューティング

### NFCリーダーが認識されない
```bash
# NFCデバイス確認
nfc-list

# PC/SCサービス確認
sudo systemctl status pcscd
```

### センサーが読み取れない
```bash
# GPIO状態確認
gpio readall

# I2C デバイス確認
i2cdetect -y 1
```

### 権限エラー
```bash
# GPIO権限追加
sudo usermod -a -G gpio pi
sudo usermod -a -G spi pi
sudo usermod -a -G i2c pi
```

### ログ確認
```bash
# アプリケーションログ
tail -f /var/log/sensor_system.log

# システムログ
sudo journalctl -u sensor-monitoring -f
```

## ⚙️ システム要件

- **OS**: Raspberry Pi OS (Debian ベース)
- **Python**: 3.7+
- **GPIO**: RPi.GPIO ライブラリ
- **NFC**: nfcpy ライブラリ
- **GUI**: tkinter (標準搭載)

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 サポート

問題や質問がある場合は、Issue を作成してください。

---

**注意**: このシステムは教育・研究目的で作成されました。商用利用の際は適切なセキュリティ監査を実施してください。
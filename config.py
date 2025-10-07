"""
システム設定ファイル
ピン配置、センサー設定、システムパラメータの管理
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class PinConfig:
    """GPIO ピン設定"""
    # PIR モーションセンサー
    MOTION_SENSOR_PIN = 18

    # HC-SR04 超音波距離センサー
    ULTRASONIC_TRIGGER_PIN = 23
    ULTRASONIC_ECHO_PIN = 24

    # AM2302 温湿度センサー
    TEMP_HUMIDITY_PIN = 4

@dataclass
class SensorConfig:
    """センサー設定"""
    # 読み取り間隔（秒）
    READING_INTERVAL = 1.0

    # 距離センサー設定
    DISTANCE_MAX_RANGE = 450  # cm
    DISTANCE_MIN_RANGE = 2    # cm
    DISTANCE_MEASUREMENT_COUNT = 3  # 平均化用測定回数

    # 温湿度センサー設定
    TEMP_MIN = -40.0  # °C
    TEMP_MAX = 80.0   # °C
    HUMIDITY_MIN = 0.0   # %
    HUMIDITY_MAX = 100.0 # %
    TEMP_HUMIDITY_RETRY_COUNT = 3

    # モーションセンサー設定
    MOTION_STABILIZATION_TIME = 2.0  # 秒

@dataclass
class NFCConfig:
    """NFC設定"""
    # NFC デバイスパス（Noneで自動検出）
    DEVICE_PATH = None

    # カード検出タイムアウト（秒）
    CARD_DETECTION_TIMEOUT = 30

    # 認証済みカードリスト（実際の運用では外部ファイルから読み込み）
    AUTHORIZED_CARDS = [
        "01020304",  # サンプルカード
        "ABCDEF01",  # 管理者カード
        "12345678"   # テストカード
    ]

@dataclass
class SystemConfig:
    """システム設定"""
    # ログファイルパス
    LOG_FILE_PATH = "/var/log/sensor_system.log"

    # ログレベル
    LOG_LEVEL = "INFO"

    # データ保存設定
    ENABLE_DATA_LOGGING = True
    DATA_LOG_PATH = "/var/log/sensor_data.json"

    # GUI設定
    GUI_WINDOW_TITLE = "センサーモニタリングシステム"
    GUI_WINDOW_SIZE = "800x600"
    GUI_UPDATE_INTERVAL = 0.1  # 秒

    # システム動作設定
    ENABLE_MOCK_MODE = False  # テスト用モックモード

@dataclass
class DisplayConfig:
    """表示設定"""
    # フォント設定
    TITLE_FONT = ('Arial', 20, 'bold')
    LABEL_FONT = ('Arial', 14, 'bold')
    VALUE_FONT = ('Arial', 16)
    SMALL_FONT = ('Arial', 10)

    # カラー設定
    BG_COLOR = '#2c3e50'
    FRAME_COLOR = '#34495e'
    TEXT_COLOR = '#ecf0f1'

    # センサー別カラー
    MOTION_COLOR = '#3498db'
    DISTANCE_COLOR = '#e67e22'
    TEMPERATURE_COLOR = '#e74c3c'
    HUMIDITY_COLOR = '#3498db'

    # ステータスカラー
    STATUS_OK_COLOR = '#2ecc71'
    STATUS_ERROR_COLOR = '#e74c3c'
    STATUS_WARNING_COLOR = '#f39c12'
    STATUS_NORMAL_COLOR = '#95a5a6'

class ConfigManager:
    """設定管理クラス"""

    def __init__(self):
        self.pins = PinConfig()
        self.sensors = SensorConfig()
        self.nfc = NFCConfig()
        self.system = SystemConfig()
        self.display = DisplayConfig()

        # 環境変数から設定を上書き
        self.load_from_environment()

    def load_from_environment(self):
        """環境変数からの設定読み込み"""

        # ピン設定
        if os.getenv('MOTION_SENSOR_PIN'):
            self.pins.MOTION_SENSOR_PIN = int(os.getenv('MOTION_SENSOR_PIN'))

        if os.getenv('ULTRASONIC_TRIGGER_PIN'):
            self.pins.ULTRASONIC_TRIGGER_PIN = int(os.getenv('ULTRASONIC_TRIGGER_PIN'))

        if os.getenv('ULTRASONIC_ECHO_PIN'):
            self.pins.ULTRASONIC_ECHO_PIN = int(os.getenv('ULTRASONIC_ECHO_PIN'))

        if os.getenv('TEMP_HUMIDITY_PIN'):
            self.pins.TEMP_HUMIDITY_PIN = int(os.getenv('TEMP_HUMIDITY_PIN'))

        # システム設定
        if os.getenv('LOG_LEVEL'):
            self.system.LOG_LEVEL = os.getenv('LOG_LEVEL')

        if os.getenv('ENABLE_MOCK_MODE'):
            self.system.ENABLE_MOCK_MODE = os.getenv('ENABLE_MOCK_MODE').lower() == 'true'

        # NFC設定
        if os.getenv('NFC_DEVICE_PATH'):
            self.nfc.DEVICE_PATH = os.getenv('NFC_DEVICE_PATH')

    def get_all_config(self):
        """全設定の取得"""
        return {
            'pins': self.pins,
            'sensors': self.sensors,
            'nfc': self.nfc,
            'system': self.system,
            'display': self.display
        }

    def validate_config(self):
        """設定の妥当性チェック"""
        errors = []

        # ピン番号の重複チェック
        pins = [
            self.pins.MOTION_SENSOR_PIN,
            self.pins.ULTRASONIC_TRIGGER_PIN,
            self.pins.ULTRASONIC_ECHO_PIN,
            self.pins.TEMP_HUMIDITY_PIN
        ]

        if len(pins) != len(set(pins)):
            errors.append("Duplicate GPIO pin assignments detected")

        # ピン番号の範囲チェック（Raspberry Pi GPIO範囲）
        valid_pins = list(range(2, 28))  # GPIO 2-27
        for pin in pins:
            if pin not in valid_pins:
                errors.append(f"Invalid GPIO pin number: {pin}")

        # センサー範囲チェック
        if self.sensors.DISTANCE_MIN_RANGE >= self.sensors.DISTANCE_MAX_RANGE:
            errors.append("Invalid distance sensor range")

        if self.sensors.TEMP_MIN >= self.sensors.TEMP_MAX:
            errors.append("Invalid temperature range")

        if self.sensors.HUMIDITY_MIN >= self.sensors.HUMIDITY_MAX:
            errors.append("Invalid humidity range")

        return errors

# デフォルト設定インスタンス
config = ConfigManager()
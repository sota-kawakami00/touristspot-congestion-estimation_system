"""
AM2302温湿度センサー制御モジュール
- 温度範囲: -40°C～80°C
- 湿度範囲: 0%～99.9%
- 通信: デジタル1-wire like
"""

import time
import logging
try:
    import Adafruit_DHT
except ImportError:
    # テスト環境用のモック
    Adafruit_DHT = None

class TemperatureHumiditySensor:
    """AM2302温湿度センサークラス"""

    def __init__(self, pin=4, sensor_type='AM2302'):
        """
        初期化
        Args:
            pin (int): データピン番号
            sensor_type (str): センサータイプ
        """
        self.pin = pin
        self.sensor_type = sensor_type
        self.logger = logging.getLogger(__name__)

        # Adafruit_DHTライブラリでのセンサータイプ設定
        if Adafruit_DHT:
            if sensor_type == 'AM2302':
                self.sensor = Adafruit_DHT.AM2302
            elif sensor_type == 'DHT22':
                self.sensor = Adafruit_DHT.DHT22
            elif sensor_type == 'DHT11':
                self.sensor = Adafruit_DHT.DHT11
            else:
                self.sensor = Adafruit_DHT.AM2302
        else:
            self.sensor = None
            self.logger.warning("Adafruit_DHT library not available, using mock data")

        self.logger.info(f"Temperature/Humidity sensor initialized ({sensor_type}, pin {pin})")

    def read_data(self):
        """
        温湿度データ読み取り
        Returns:
            tuple: (temperature_celsius, humidity_percent) or (None, None) if error
        """
        try:
            if self.sensor:
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin, retries=3)

                if humidity is not None and temperature is not None:
                    # データ検証
                    if -40 <= temperature <= 80 and 0 <= humidity <= 100:
                        self.logger.debug(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
                        return round(temperature, 1), round(humidity, 1)
                    else:
                        self.logger.warning(f"Data out of range: T={temperature}, H={humidity}")
                        return None, None
                else:
                    self.logger.warning("Failed to read sensor data")
                    return None, None
            else:
                # モックデータ（テスト用）
                import random
                temperature = round(20 + random.uniform(-5, 15), 1)
                humidity = round(50 + random.uniform(-20, 30), 1)
                self.logger.debug(f"Mock data - Temperature: {temperature}°C, Humidity: {humidity}%")
                return temperature, humidity

        except Exception as e:
            self.logger.error(f"Temperature/Humidity sensor error: {e}")
            return None, None

    def read_temperature(self):
        """
        温度のみ読み取り
        Returns:
            float: 温度（摂氏）、エラー時はNone
        """
        temperature, _ = self.read_data()
        return temperature

    def read_humidity(self):
        """
        湿度のみ読み取り
        Returns:
            float: 湿度（％）、エラー時はNone
        """
        _, humidity = self.read_data()
        return humidity

    def read_multiple(self, count=3, delay=2.0):
        """
        複数回測定して平均値を返す
        Args:
            count (int): 測定回数
            delay (float): 測定間隔（秒）
        Returns:
            tuple: (average_temperature, average_humidity)
        """
        temperatures = []
        humidities = []

        for i in range(count):
            temp, hum = self.read_data()
            if temp is not None and hum is not None:
                temperatures.append(temp)
                humidities.append(hum)
            time.sleep(delay)

        if temperatures and humidities:
            avg_temp = sum(temperatures) / len(temperatures)
            avg_humidity = sum(humidities) / len(humidities)
            self.logger.debug(f"Average from {len(temperatures)} measurements: T={avg_temp:.1f}°C, H={avg_humidity:.1f}%")
            return round(avg_temp, 1), round(avg_humidity, 1)
        else:
            self.logger.warning("No valid temperature/humidity measurements")
            return None, None

    def get_status(self):
        """
        センサー状態取得
        Returns:
            dict: センサー状態情報
        """
        temperature, humidity = self.read_data()
        return {
            'pin': self.pin,
            'sensor_type': self.sensor_type,
            'temperature_celsius': temperature,
            'humidity_percent': humidity,
            'status': 'ok' if temperature is not None and humidity is not None else 'error',
            'timestamp': time.time()
        }

    def cleanup(self):
        """リソースクリーンアップ"""
        try:
            self.logger.info("Temperature/Humidity sensor cleanup completed")
        except Exception as e:
            self.logger.error(f"Temperature/Humidity sensor cleanup error: {e}")

    def __del__(self):
        """デストラクタ"""
        self.cleanup()
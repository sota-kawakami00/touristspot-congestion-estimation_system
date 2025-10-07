"""
HC-SR04超音波距離センサー制御モジュール
- 測定範囲: 0.02m-4.5m
- 動作電圧: 3V-5.5V
- インターフェース: GPIO
"""

import RPi.GPIO as GPIO
import time
import logging

class DistanceSensor:
    """HC-SR04超音波距離センサークラス"""

    def __init__(self, trigger_pin=23, echo_pin=24):
        """
        初期化
        Args:
            trigger_pin (int): トリガーピン番号
            echo_pin (int): エコーピン番号
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.logger = logging.getLogger(__name__)

        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        # 初期状態をLowに設定
        GPIO.output(self.trigger_pin, False)
        time.sleep(0.1)

        self.logger.info(f"Distance sensor initialized (Trigger: {trigger_pin}, Echo: {echo_pin})")

    def measure_distance(self):
        """
        距離測定
        Returns:
            float: 距離（cm）、エラー時は-1
        """
        try:
            # トリガーパルス送信
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)  # 10μs
            GPIO.output(self.trigger_pin, False)

            # エコー受信開始時刻
            pulse_start = time.time()
            timeout_start = pulse_start
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if pulse_start - timeout_start > 0.1:  # 100msタイムアウト
                    self.logger.warning("Distance sensor timeout waiting for pulse start")
                    return -1

            # エコー受信終了時刻
            pulse_end = time.time()
            timeout_end = pulse_end
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if pulse_end - timeout_end > 0.1:  # 100msタイムアウト
                    self.logger.warning("Distance sensor timeout waiting for pulse end")
                    return -1

            # 距離計算（音速: 343m/s）
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # (343 * 100) / 2

            # 有効範囲チェック
            if 2 <= distance <= 450:
                self.logger.debug(f"Distance measured: {distance:.2f}cm")
                return round(distance, 2)
            else:
                self.logger.warning(f"Distance out of range: {distance:.2f}cm")
                return -1

        except Exception as e:
            self.logger.error(f"Distance sensor error: {e}")
            return -1

    def measure_multiple(self, count=5, delay=0.1):
        """
        複数回測定して平均値を返す
        Args:
            count (int): 測定回数
            delay (float): 測定間隔（秒）
        Returns:
            float: 平均距離（cm）
        """
        measurements = []

        for i in range(count):
            distance = self.measure_distance()
            if distance > 0:
                measurements.append(distance)
            time.sleep(delay)

        if measurements:
            avg_distance = sum(measurements) / len(measurements)
            self.logger.debug(f"Average distance from {len(measurements)} measurements: {avg_distance:.2f}cm")
            return round(avg_distance, 2)
        else:
            self.logger.warning("No valid distance measurements")
            return -1

    def get_status(self):
        """
        センサー状態取得
        Returns:
            dict: センサー状態情報
        """
        distance = self.measure_distance()
        return {
            'trigger_pin': self.trigger_pin,
            'echo_pin': self.echo_pin,
            'distance_cm': distance,
            'status': 'ok' if distance > 0 else 'error',
            'timestamp': time.time()
        }

    def cleanup(self):
        """リソースクリーンアップ"""
        try:
            GPIO.cleanup([self.trigger_pin, self.echo_pin])
            self.logger.info("Distance sensor cleanup completed")
        except Exception as e:
            self.logger.error(f"Distance sensor cleanup error: {e}")

    def __del__(self):
        """デストラクタ"""
        self.cleanup()
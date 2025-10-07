"""
PIRモーションセンサー（人感センサー）制御モジュール
- 検出角度: 115度
- 検出距離: 最大8m
- 動作電圧: 3.3V-12V
"""

import RPi.GPIO as GPIO
import time
import logging

class MotionSensor:
    """PIRモーションセンサークラス"""

    def __init__(self, pin=18):
        """
        初期化
        Args:
            pin (int): GPIO ピン番号
        """
        self.pin = pin
        self.logger = logging.getLogger(__name__)

        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

        # センサー安定化待ち
        self.logger.info(f"PIR sensor initializing on pin {self.pin}...")
        time.sleep(2)  # センサー安定化のため2秒待機
        self.logger.info("PIR sensor ready")

    def detect_motion(self):
        """
        モーション検出
        Returns:
            bool: モーション検出時True、未検出時False
        """
        try:
            motion_state = GPIO.input(self.pin)
            if motion_state:
                self.logger.debug("Motion detected!")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Motion sensor error: {e}")
            return False

    def wait_for_motion(self, timeout=None):
        """
        モーション検出まで待機
        Args:
            timeout (float): タイムアウト時間（秒）
        Returns:
            bool: モーション検出時True、タイムアウト時False
        """
        start_time = time.time()

        while True:
            if self.detect_motion():
                return True

            if timeout and (time.time() - start_time) > timeout:
                return False

            time.sleep(0.1)

    def get_status(self):
        """
        センサー状態取得
        Returns:
            dict: センサー状態情報
        """
        return {
            'pin': self.pin,
            'motion_detected': self.detect_motion(),
            'timestamp': time.time()
        }

    def cleanup(self):
        """リソースクリーンアップ"""
        try:
            GPIO.cleanup(self.pin)
            self.logger.info("PIR sensor cleanup completed")
        except Exception as e:
            self.logger.error(f"PIR sensor cleanup error: {e}")

    def __del__(self):
        """デストラクタ"""
        self.cleanup()
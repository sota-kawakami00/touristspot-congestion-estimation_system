#!/usr/bin/env python3
"""
Raspberry Pi Sensor Monitoring System
センサー値を読み取り、モニターに表示するメインシステム
"""

import time
import threading
import queue
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import logging

# センサーモジュールのインポート
from sensors.motion_sensor import MotionSensor
from sensors.distance_sensor import DistanceSensor
from sensors.temperature_humidity_sensor import TemperatureHumiditySensor
from auth.nfc_reader import NFCReader
from display.gui_display import SensorGUI
from config import config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sensor_system.log'),
        logging.StreamHandler()
    ]
)

class SensorMonitoringSystem:
    """メインのセンサーモニタリングシステム"""

    def __init__(self, headless=False, skip_auth=False):
        self.logger = logging.getLogger(__name__)
        self.is_authenticated = False
        self.is_running = False
        self.data_queue = queue.Queue()
        self.headless = headless
        self.skip_auth = skip_auth

        # センサーの初期化
        self.motion_sensor = MotionSensor(pin=config.pins.MOTION_SENSOR_PIN)
        self.distance_sensor = DistanceSensor(
            trigger_pin=config.pins.ULTRASONIC_TRIGGER_PIN,
            echo_pin=config.pins.ULTRASONIC_ECHO_PIN
        )
        self.temp_humidity_sensor = TemperatureHumiditySensor(pin=config.pins.TEMP_HUMIDITY_PIN)

        # NFC認証システムの初期化
        self.nfc_reader = NFCReader()

        # GUI初期化（ヘッドレスモードでない場合のみ）
        self.gui = None
        if not headless:
            try:
                self.gui = SensorGUI(self.data_queue)
            except Exception as e:
                self.logger.warning(f"GUI initialization failed: {e}. Running in headless mode.")
                self.headless = True

        self.logger.info(f"Sensor Monitoring System initialized (headless: {self.headless})")

    def authenticate_user(self):
        """NFC認証を実行"""
        self.logger.info("Waiting for NFC authentication...")
        try:
            if self.nfc_reader.wait_for_card():
                card_id = self.nfc_reader.read_card_id()
                if self.nfc_reader.validate_card(card_id):
                    self.is_authenticated = True
                    self.logger.info(f"Authentication successful for card: {card_id}")
                    return True
                else:
                    self.logger.warning(f"Authentication failed for card: {card_id}")
                    return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    def read_sensors(self):
        """センサーからデータを読み取る"""
        sensor_data = {
            'timestamp': datetime.now().isoformat(),
            'motion_detected': False,
            'distance_cm': 0.0,
            'temperature_c': 0.0,
            'humidity_percent': 0.0,
            'system_status': 'running'
        }

        try:
            # モーションセンサー読み取り
            sensor_data['motion_detected'] = self.motion_sensor.detect_motion()

            # 距離センサー読み取り
            sensor_data['distance_cm'] = self.distance_sensor.measure_distance()

            # 温湿度センサー読み取り
            temp, humidity = self.temp_humidity_sensor.read_data()
            sensor_data['temperature_c'] = temp
            sensor_data['humidity_percent'] = humidity

        except Exception as e:
            self.logger.error(f"Sensor reading error: {e}")
            sensor_data['system_status'] = 'error'

        return sensor_data

    def sensor_loop(self):
        """センサー読み取りメインループ"""
        while self.is_running:
            if self.is_authenticated:
                data = self.read_sensors()
                self.data_queue.put(data)
                self.logger.debug(f"Sensor data: {data}")

            time.sleep(config.sensors.READING_INTERVAL)  # 設定間隔で読み取り

    def run(self):
        """システムメイン実行"""
        self.logger.info("Starting Sensor Monitoring System")

        # 認証待ち（スキップオプションがある場合は省略）
        if self.skip_auth:
            print("認証をスキップしました（テストモード）")
            self.is_authenticated = True
        else:
            print("NFCカードをタッチしてください...")
            if not self.authenticate_user():
                print("認証に失敗しました。システムを終了します。")
                return

        print("認証成功！システムを開始します...")
        self.is_running = True

        # センサー読み取りスレッド開始
        sensor_thread = threading.Thread(target=self.sensor_loop, daemon=True)
        sensor_thread.start()

        # GUI開始（ヘッドレスモードでない場合）
        try:
            if self.gui and not self.headless:
                self.gui.run()
            else:
                # ヘッドレスモード：無限ループでセンサーデータを読み続ける
                self.logger.info("Running in headless mode")
                while self.is_running:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("System interrupted by user")
        finally:
            self.shutdown()

    def shutdown(self):
        """システム終了処理"""
        self.logger.info("Shutting down system...")
        self.is_running = False

        # センサークリーンアップ
        self.motion_sensor.cleanup()
        self.distance_sensor.cleanup()
        self.temp_humidity_sensor.cleanup()
        self.nfc_reader.cleanup()

        self.logger.info("System shutdown complete")

def main():
    """メイン関数"""
    import os
    import sys

    # systemdサービスから実行される場合、または --headless引数がある場合はヘッドレスモードで実行
    headless = '--headless' in sys.argv or os.environ.get('DISPLAY') is None
    skip_auth = '--skip-auth' in sys.argv

    try:
        system = SensorMonitoringSystem(headless=headless, skip_auth=skip_auth)
        system.run()
    except Exception as e:
        logging.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    main()
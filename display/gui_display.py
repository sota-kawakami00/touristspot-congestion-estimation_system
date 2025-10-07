"""
センサーデータ表示用GUIモジュール
Tkinterを使用してリアルタイムでセンサーデータを表示
"""

import tkinter as tk
from tkinter import ttk, messagebox
import queue
import threading
import time
from datetime import datetime
import logging

class SensorGUI:
    """センサーデータ表示GUI"""

    def __init__(self, data_queue):
        """
        初期化
        Args:
            data_queue (queue.Queue): センサーデータキュー
        """
        self.data_queue = data_queue
        self.logger = logging.getLogger(__name__)
        self.is_running = False

        # メインウィンドウ設定
        self.root = tk.Tk()
        self.root.title("センサーモニタリングシステム")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')

        # フォント設定
        self.title_font = ('Arial', 20, 'bold')
        self.label_font = ('Arial', 14, 'bold')
        self.value_font = ('Arial', 16)
        self.small_font = ('Arial', 10)

        # データ保存用
        self.current_data = {
            'timestamp': '',
            'motion_detected': False,
            'distance_cm': 0.0,
            'temperature_c': 0.0,
            'humidity_percent': 0.0,
            'system_status': 'waiting'
        }

        self.setup_gui()
        self.logger.info("GUI initialized")

    def setup_gui(self):
        """GUI要素の設定"""

        # タイトル
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text="🔍 センサーモニタリングシステム",
            font=self.title_font,
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack()

        # メインコンテナ
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # センサーデータ表示エリア
        self.setup_sensor_display(main_frame)

        # ステータス表示エリア
        self.setup_status_display(main_frame)

        # 閉じるボタン
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=10)

        close_button = tk.Button(
            button_frame,
            text="システム終了",
            command=self.close_application,
            font=self.label_font,
            bg='#e74c3c',
            fg='white',
            width=15,
            height=2
        )
        close_button.pack()

    def setup_sensor_display(self, parent):
        """センサーデータ表示エリアの設定"""

        # センサーデータフレーム
        sensor_frame = tk.LabelFrame(
            parent,
            text="センサーデータ",
            font=self.label_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=20,
            pady=20
        )
        sensor_frame.pack(fill='x', pady=10)

        # グリッドレイアウト設定
        for i in range(4):
            sensor_frame.columnconfigure(i, weight=1)

        # モーションセンサー
        motion_frame = tk.Frame(sensor_frame, bg='#34495e')
        motion_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        tk.Label(
            motion_frame,
            text="🚶 人感センサー",
            font=self.label_font,
            bg='#34495e',
            fg='#3498db'
        ).pack()

        self.motion_label = tk.Label(
            motion_frame,
            text="未検出",
            font=self.value_font,
            bg='#34495e',
            fg='#95a5a6'
        )
        self.motion_label.pack()

        # 距離センサー
        distance_frame = tk.Frame(sensor_frame, bg='#34495e')
        distance_frame.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        tk.Label(
            distance_frame,
            text="📏 距離センサー",
            font=self.label_font,
            bg='#34495e',
            fg='#e67e22'
        ).pack()

        self.distance_label = tk.Label(
            distance_frame,
            text="-- cm",
            font=self.value_font,
            bg='#34495e',
            fg='#95a5a6'
        )
        self.distance_label.pack()

        # 温度センサー
        temp_frame = tk.Frame(sensor_frame, bg='#34495e')
        temp_frame.grid(row=0, column=2, padx=10, pady=10, sticky='ew')

        tk.Label(
            temp_frame,
            text="🌡️ 温度",
            font=self.label_font,
            bg='#34495e',
            fg='#e74c3c'
        ).pack()

        self.temp_label = tk.Label(
            temp_frame,
            text="-- °C",
            font=self.value_font,
            bg='#34495e',
            fg='#95a5a6'
        )
        self.temp_label.pack()

        # 湿度センサー
        humidity_frame = tk.Frame(sensor_frame, bg='#34495e')
        humidity_frame.grid(row=0, column=3, padx=10, pady=10, sticky='ew')

        tk.Label(
            humidity_frame,
            text="💧 湿度",
            font=self.label_font,
            bg='#34495e',
            fg='#3498db'
        ).pack()

        self.humidity_label = tk.Label(
            humidity_frame,
            text="-- %",
            font=self.value_font,
            bg='#34495e',
            fg='#95a5a6'
        )
        self.humidity_label.pack()

    def setup_status_display(self, parent):
        """ステータス表示エリアの設定"""

        # ステータスフレーム
        status_frame = tk.LabelFrame(
            parent,
            text="システム状態",
            font=self.label_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=20,
            pady=20
        )
        status_frame.pack(fill='x', pady=10)

        # 最終更新時刻
        time_frame = tk.Frame(status_frame, bg='#34495e')
        time_frame.pack(anchor='w', pady=5)

        tk.Label(
            time_frame,
            text="最終更新:",
            font=self.label_font,
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side='left')

        self.time_label = tk.Label(
            time_frame,
            text="--:--:--",
            font=self.value_font,
            bg='#34495e',
            fg='#95a5a6'
        )
        self.time_label.pack(side='left', padx=(10, 0))

        # システムステータス
        status_frame_inner = tk.Frame(status_frame, bg='#34495e')
        status_frame_inner.pack(anchor='w', pady=5)

        tk.Label(
            status_frame_inner,
            text="ステータス:",
            font=self.label_font,
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side='left')

        self.status_label = tk.Label(
            status_frame_inner,
            text="待機中",
            font=self.value_font,
            bg='#34495e',
            fg='#f39c12'
        )
        self.status_label.pack(side='left', padx=(10, 0))

        # データログ表示エリア
        log_frame = tk.LabelFrame(
            parent,
            text="データログ（最新10件）",
            font=self.label_font,
            bg='#34495e',
            fg='#ecf0f1',
            padx=10,
            pady=10
        )
        log_frame.pack(fill='both', expand=True, pady=10)

        # スクロール可能なテキストエリア
        self.log_text = tk.Text(
            log_frame,
            height=8,
            bg='#2c3e50',
            fg='#ecf0f1',
            font=self.small_font,
            state='disabled'
        )
        scrollbar = tk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def update_display(self, data):
        """表示データ更新"""
        self.current_data = data

        # モーションセンサー表示更新
        if data['motion_detected']:
            self.motion_label.config(text="検出！", fg='#e74c3c')
        else:
            self.motion_label.config(text="未検出", fg='#95a5a6')

        # 距離センサー表示更新
        if data['distance_cm'] > 0:
            self.distance_label.config(text=f"{data['distance_cm']:.1f} cm", fg='#e67e22')
        else:
            self.distance_label.config(text="-- cm", fg='#95a5a6')

        # 温度表示更新
        if data['temperature_c'] is not None:
            self.temp_label.config(text=f"{data['temperature_c']:.1f} °C", fg='#e74c3c')
        else:
            self.temp_label.config(text="-- °C", fg='#95a5a6')

        # 湿度表示更新
        if data['humidity_percent'] is not None:
            self.humidity_label.config(text=f"{data['humidity_percent']:.1f} %", fg='#3498db')
        else:
            self.humidity_label.config(text="-- %", fg='#95a5a6')

        # 時刻表示更新
        timestamp = datetime.fromisoformat(data['timestamp'])
        time_str = timestamp.strftime("%H:%M:%S")
        self.time_label.config(text=time_str, fg='#2ecc71')

        # ステータス表示更新
        status = data['system_status']
        if status == 'running':
            self.status_label.config(text="正常動作", fg='#2ecc71')
        elif status == 'error':
            self.status_label.config(text="エラー", fg='#e74c3c')
        else:
            self.status_label.config(text="待機中", fg='#f39c12')

        # ログ追加
        self.add_log_entry(data)

    def add_log_entry(self, data):
        """ログエントリ追加"""
        timestamp = datetime.fromisoformat(data['timestamp'])
        time_str = timestamp.strftime("%H:%M:%S")

        motion_text = "検出" if data['motion_detected'] else "未検出"
        distance_text = f"{data['distance_cm']:.1f}cm" if data['distance_cm'] > 0 else "--"
        temp_text = f"{data['temperature_c']:.1f}°C" if data['temperature_c'] is not None else "--"
        humidity_text = f"{data['humidity_percent']:.1f}%" if data['humidity_percent'] is not None else "--"

        log_entry = f"{time_str} | 人感:{motion_text} | 距離:{distance_text} | 温度:{temp_text} | 湿度:{humidity_text}\n"

        # ログテキストに追加
        self.log_text.config(state='normal')
        self.log_text.insert('end', log_entry)

        # 最新10件のみ保持
        lines = self.log_text.get('1.0', 'end').split('\n')
        if len(lines) > 11:  # 改行により空行が1つ追加されるため11行でチェック
            self.log_text.delete('1.0', '2.0')

        self.log_text.config(state='disabled')
        self.log_text.see('end')

    def data_update_loop(self):
        """データ更新ループ"""
        while self.is_running:
            try:
                # キューからデータ取得（ノンブロッキング）
                data = self.data_queue.get_nowait()
                self.update_display(data)
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Display update error: {e}")

            time.sleep(0.1)

    def close_application(self):
        """アプリケーション終了"""
        if messagebox.askyesno("確認", "システムを終了しますか？"):
            self.is_running = False
            self.root.quit()

    def run(self):
        """GUI実行"""
        self.is_running = True

        # データ更新スレッド開始
        update_thread = threading.Thread(target=self.data_update_loop, daemon=True)
        update_thread.start()

        # ウィンドウ閉じるイベント
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        self.logger.info("GUI started")

        # メインループ開始
        self.root.mainloop()

        self.is_running = False
        self.logger.info("GUI closed")
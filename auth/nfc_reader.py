"""
SONY NFC リーダー制御モジュール
FeliCa/NFCカード認証システム
"""

import time
import logging
import hashlib
try:
    import nfc
    from nfc.clf import RemoteTarget
except ImportError:
    # テスト環境用のモック
    nfc = None

class NFCReader:
    """SONY NFCリーダー制御クラス"""

    def __init__(self, device_path=None):
        """
        初期化
        Args:
            device_path (str): NFCデバイスパス（Noneの場合は自動検出）
        """
        self.device_path = device_path
        self.clf = None
        self.logger = logging.getLogger(__name__)
        self.authorized_cards = set()  # 認証済みカードID

        # デフォルト認証カード設定（実際の運用では外部ファイルから読み込み）
        self.load_authorized_cards()

        self.initialize_reader()

    def initialize_reader(self):
        """NFCリーダーの初期化"""
        try:
            if nfc:
                if self.device_path:
                    self.clf = nfc.ContactlessFrontend(self.device_path)
                else:
                    self.clf = nfc.ContactlessFrontend()

                if self.clf:
                    self.logger.info(f"NFC reader initialized: {self.clf}")
                    return True
                else:
                    self.logger.error("Failed to initialize NFC reader")
                    return False
            else:
                self.logger.warning("nfc library not available, using mock mode")
                return True

        except Exception as e:
            self.logger.error(f"NFC reader initialization error: {e}")
            return False

    def load_authorized_cards(self):
        """認証カード情報の読み込み"""
        # デフォルトの認証カード（実際の運用では設定ファイルから読み込み）
        default_cards = [
            "01020304",  # サンプルカードID
            "ABCDEF01",  # 管理者カード
            "12345678"   # テストカード
        ]

        for card_id in default_cards:
            self.authorized_cards.add(self.hash_card_id(card_id))

        self.logger.info(f"Loaded {len(self.authorized_cards)} authorized cards")

    def hash_card_id(self, card_id):
        """
        カードIDのハッシュ化（セキュリティ向上）
        Args:
            card_id (str): カードID
        Returns:
            str: ハッシュ化されたカードID
        """
        return hashlib.sha256(card_id.encode()).hexdigest()[:16]

    def wait_for_card(self, timeout=30):
        """
        NFCカードの検出を待機
        Args:
            timeout (int): タイムアウト時間（秒）
        Returns:
            bool: カード検出時True、タイムアウト時False
        """
        if not nfc:
            # モックモード：2秒待機してTrue
            self.logger.info("Mock mode: simulating card detection")
            time.sleep(2)
            return True

        try:
            self.logger.info("Waiting for NFC card...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                if self.clf:
                    # カード検出試行
                    target = self.clf.sense(
                        RemoteTarget('212F'),  # FeliCa
                        RemoteTarget('106A'),  # Type A
                        RemoteTarget('106B'),  # Type B
                        iterations=1,
                        interval=0.1
                    )

                    if target:
                        self.logger.info(f"Card detected: {target}")
                        return True

                time.sleep(0.1)

            self.logger.warning("Card detection timeout")
            return False

        except Exception as e:
            self.logger.error(f"Card detection error: {e}")
            return False

    def read_card_id(self):
        """
        カードIDの読み取り
        Returns:
            str: カードID、エラー時はNone
        """
        if not nfc:
            # モックモード：テスト用カードID返却
            mock_card_id = "01020304"
            self.logger.info(f"Mock mode: returning card ID {mock_card_id}")
            return mock_card_id

        try:
            if self.clf:
                target = self.clf.sense(
                    RemoteTarget('212F'),  # FeliCa
                    RemoteTarget('106A'),  # Type A
                    RemoteTarget('106B'),  # Type B
                    iterations=3,
                    interval=0.1
                )

                if target:
                    if hasattr(target, 'idm'):
                        # FeliCa IDm
                        card_id = target.idm.hex().upper()
                        self.logger.debug(f"FeliCa IDm: {card_id}")
                        return card_id
                    elif hasattr(target, 'uid'):
                        # NFC Type A/B UID
                        card_id = target.uid.hex().upper()
                        self.logger.debug(f"NFC UID: {card_id}")
                        return card_id
                    else:
                        self.logger.warning("Unknown card type")
                        return None
                else:
                    self.logger.warning("No card detected for ID reading")
                    return None
            else:
                self.logger.error("NFC reader not initialized")
                return None

        except Exception as e:
            self.logger.error(f"Card ID reading error: {e}")
            return None

    def validate_card(self, card_id):
        """
        カードの認証
        Args:
            card_id (str): カードID
        Returns:
            bool: 認証成功時True、失敗時False
        """
        if not card_id:
            return False

        try:
            hashed_id = self.hash_card_id(card_id)
            is_authorized = hashed_id in self.authorized_cards

            if is_authorized:
                self.logger.info(f"Card authentication successful: {card_id[:8]}...")
            else:
                self.logger.warning(f"Card authentication failed: {card_id[:8]}...")

            return is_authorized

        except Exception as e:
            self.logger.error(f"Card validation error: {e}")
            return False

    def add_authorized_card(self, card_id):
        """
        認証カードの追加
        Args:
            card_id (str): 追加するカードID
        """
        hashed_id = self.hash_card_id(card_id)
        self.authorized_cards.add(hashed_id)
        self.logger.info(f"Added authorized card: {card_id[:8]}...")

    def remove_authorized_card(self, card_id):
        """
        認証カードの削除
        Args:
            card_id (str): 削除するカードID
        """
        hashed_id = self.hash_card_id(card_id)
        if hashed_id in self.authorized_cards:
            self.authorized_cards.remove(hashed_id)
            self.logger.info(f"Removed authorized card: {card_id[:8]}...")
        else:
            self.logger.warning(f"Card not found in authorized list: {card_id[:8]}...")

    def get_reader_info(self):
        """
        リーダー情報の取得
        Returns:
            dict: リーダー情報
        """
        info = {
            'device_path': self.device_path,
            'initialized': self.clf is not None,
            'authorized_cards_count': len(self.authorized_cards),
            'library_available': nfc is not None
        }

        if self.clf and hasattr(self.clf, 'device'):
            info['device_info'] = str(self.clf.device)

        return info

    def test_authentication_flow(self):
        """
        認証フロー全体のテスト
        Returns:
            bool: テスト成功時True
        """
        try:
            self.logger.info("Testing NFC authentication flow...")

            # カード検出待機
            if not self.wait_for_card(timeout=10):
                self.logger.error("Test failed: No card detected")
                return False

            # カードID読み取り
            card_id = self.read_card_id()
            if not card_id:
                self.logger.error("Test failed: Could not read card ID")
                return False

            # 認証
            if self.validate_card(card_id):
                self.logger.info("Test passed: Authentication successful")
                return True
            else:
                self.logger.warning("Test completed: Card not authorized")
                return False

        except Exception as e:
            self.logger.error(f"Authentication test error: {e}")
            return False

    def cleanup(self):
        """リソースクリーンアップ"""
        try:
            if self.clf:
                self.clf.close()
                self.clf = None
                self.logger.info("NFC reader cleanup completed")
        except Exception as e:
            self.logger.error(f"NFC reader cleanup error: {e}")

    def __del__(self):
        """デストラクタ"""
        self.cleanup()
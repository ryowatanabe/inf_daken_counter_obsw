import ctypes
from ctypes import windll,wintypes,create_string_buffer
from datetime import datetime
from PIL import Image
from logging import getLogger
from os.path import exists,basename
import numpy as np

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from resources import load_resource_serialized

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
PW_CLIENTONLY = 1

"""
screenshot.py

このスクリプトは、スクリーンショットのキャプチャや画像処理を行うためのものです。

主な機能:
- スクリーンショットの取得
- 取得した画像の加工や保存
- スクリーン情報の取得
"""

class BITMAPINFOHEADER(ctypes.Structure):
    """
    スクリーンショットのキャプチャに必要なビットマップ情報のヘッダーを定義する構造体。
    """
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class RGBQUAD(ctypes.Structure):
    """
    RGB カラー情報を格納する構造体。
    """
    _fields_ = [
        ('rgbRed', ctypes.c_byte),
        ('rgbGreen', ctypes.c_byte),
        ('rgbBlue', ctypes.c_byte),
        ('rgbReserved', ctypes.c_byte),
    ]

class BITMAPINFO(ctypes.Structure):
    """
    ビットマップ情報を格納する構造体。
    """
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.POINTER(RGBQUAD))
    ]

class Screen:
    """
    スクリーンショットの画像データとファイル名を格納するクラス。
    """
    def __init__(self, np_value, filename):
        """
        初期化メソッド。

        引数:
        - np_value: 画像データ (numpy array)
        - filename: ファイル名 (str)
        """
        self.np_value = np_value

        self.original = Image.fromarray(np_value)
        self.filename = filename

class Capture:
    """
    スクリーンショットをキャプチャするためのクラス。
    """
    def __init__(self, width, height):
        """
        初期化メソッド。

        引数:
        - width: キャプチャする幅 (int)
        - height: キャプチャする高さ (int)
        """
        self.width = width
        self.height = height

        self.bmi = BITMAPINFO()
        self.bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.bmi.bmiHeader.biWidth = self.width
        self.bmi.bmiHeader.biHeight = self.height
        self.bmi.bmiHeader.biPlanes = 1
        self.bmi.bmiHeader.biBitCount = 24
        self.bmi.bmiHeader.biCompression = 0
        self.bmi.bmiHeader.biSizeImage = 0

        self.screen = windll.gdi32.CreateDCW("DISPLAY", None, None, None)
        self.screen_copy = windll.gdi32.CreateCompatibleDC(self.screen)
        self.bitmap = windll.gdi32.CreateCompatibleBitmap(self.screen, self.width, self.height)

        windll.gdi32.SelectObject(self.screen_copy, self.bitmap)

        self.buffer = create_string_buffer(self.height * self.width * 3)
    
    def shot(self, left, top):
        """
        指定された位置のスクリーンショットを取得します。

        引数:
        - left: 左上の x 座標 (int)
        - top: 左上の y 座標 (int)

        戻り値:
        - 取得した画像データ (numpy array)
        """
        windll.gdi32.BitBlt(self.screen_copy, 0, 0, self.width, self.height, self.screen, left, top, SRCCOPY)
        windll.gdi32.GetDIBits(self.screen_copy, self.bitmap, 0, self.height, ctypes.pointer(self.buffer), ctypes.pointer(self.bmi), DIB_RGB_COLORS)

        return np.array(bytearray(self.buffer)).reshape(self.height, self.width, 3)

    def __del__(self):
        """
        リソースを解放するデストラクタ。
        """
        windll.gdi32.DeleteObject(self.bitmap)
        windll.gdi32.DeleteDC(self.screen_copy)
        windll.gdi32.DeleteDC(self.screen)

        logger.debug('Called Screenshot destuctor.')

class Screenshot:
    """
    スクリーンショットの管理と操作を行うクラス。
    """
    xy = None
    screentable = load_resource_serialized('get_screen')
    np_value = None

    def __init__(self):
        """
        初期化メソッド。
        """
        self.checkscreens = [(screen, (areas['left'], areas['top']), Capture(areas['width'], areas['height']), self.screentable[screen]) for screen, areas in define.screens.items()]
        self.capture = Capture(define.width, define.height)

    def __del__(self):
        """
        リソースを解放するデストラクタ。
        """
        for screen, pos, capture, value in self.checkscreens:
            del capture
        del self.capture

    def get_screen(self):
        """
        現在のスクリーン情報を取得します。

        戻り値:
        - スクリーン情報 (str) または None
        """
        if self.xy is None:
            return None
        
        results = []
        for screen, pos, capture, value in self.checkscreens:
            x = self.xy[0] + pos[0]
            y = self.xy[1] + pos[1]

            if np.sum(capture.shot(x, y)) == value:
                results.append(screen)
        
        if len(results) != 1:
            return None

        return results[0]

    def shot(self):
        """
        スクリーンショットを取得します。

        戻り値:
        - 成功した場合は True、それ以外は False
        """
        if self.xy is None:
            return False
        
        self.np_value = self.capture.shot(self.xy[0], self.xy[1])[::-1, :, ::-1]
        return True

    def get_image(self):
        """
        取得したスクリーンショットを PIL.Image オブジェクトとして返します。

        戻り値:
        - 画像データ (PIL.Image) または None
        """
        if self.np_value is None:
            return None
        
        return Image.fromarray(self.np_value)

    def get_resultscreen(self):
        """
        スクリーンショットの結果を Screen オブジェクトとして返します。

        戻り値:
        - Screen オブジェクト
        """
        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(self.np_value, filename)

def open_screenimage(filepath):
    """
    指定されたファイルパスからスクリーンショット画像を開きます。

    引数:
    - filepath: ファイルパス (str)

    戻り値:
    - Screen オブジェクト または None
    """
    if not exists(filepath):
        return None
    
    image = Image.open(filepath).convert('RGB')
    filename = basename(filepath)

    return Screen(np.array(image), filename)

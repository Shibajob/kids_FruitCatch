import os
import sys

# PyInstaller で実行する場合と通常の Python 実行時で、
# 画像の配置先を共通で参照できるようにする。
BASE_DIR = getattr(
    sys,
    "_MEIPASS",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# ゲーム画面の基本設定。
WINDOW_NAME = "Kids Fruit Catch"
WIDTH = 1280
HEIGHT = 720
FULLSCREEN = True

# フルーツの落下速度と生成間隔の設定。
FRUIT_SIZE = 120
FRUIT_RADIUS = FRUIT_SIZE // 2
SPAWN_INTERVAL = 0.8
FRUIT_SPEED_MIN = 4
FRUIT_SPEED_MAX = 8

# 姿勢検出の判定閾値と表示設定。
SHOW_BODY_POINTS = False
BODY_HIT_RADIUS = 90
POSE_VISIBILITY = 0.5

# スコアとエフェクトの設定。
SCORE_PER_FRUIT = 1
GOOD_EFFECT_TIME = 1.0

# ゲームで使う画像の保存先。
FRUIT_DIR = os.path.join(BASE_DIR, "images", "fruits")

# OpenCV の BGR カラー定義。
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from kids_FruitCatch import settings
from kids_FruitCatch.game import FruitGame


def _load_japanese_font():
    font_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for filename in ("meiryo.ttc", "YuGothM.ttc", "msgothic.ttc"):
        path = os.path.join(font_dir, filename)
        if os.path.isfile(path):
            return ImageFont.truetype(path, 26)

    raise FileNotFoundError(f"日本語フォントが見つかりません: {font_dir}")


def _draw_japanese_text(frame, text, position, font):
    x, y = position
    width, height = 630, 48
    panel = Image.new("RGB", (width, height), (255, 250, 245))
    draw = ImageDraw.Draw(panel)

    while font.getlength(text) > width:
        font = ImageFont.truetype(font.path, font.size - 1)

    draw.text((0, 2), text, font=font, fill=(95, 85, 70))
    frame[y:y + height, x:x + width] = cv2.cvtColor(
        np.asarray(panel),
        cv2.COLOR_RGB2BGR,
    )


def _load_title_fruits():
    fruits = []
    for filename, size, position in (
        ("orange.png", (280, 280), (820, 165)),
        ("apple.png", (235, 235), (1010, 355)),
    ):
        path = os.path.join(settings.FRUIT_DIR, filename)
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"タイトル画面用の画像を読み込めません: {path}")

        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        fruits.append((image, position))
    return fruits


def _draw_title_background(frame):
    frame[:] = (255, 220, 180)

    for x, y, width, height in (
        (180, 100, 150, 55),
        (600, 85, 190, 65),
        (1100, 125, 145, 52),
    ):
        cv2.ellipse(frame, (x, y), (width, height), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(frame, (x - width // 2, y + 8), height // 2, (255, 255, 255), -1)
        cv2.circle(frame, (x + width // 2, y + 8), height // 2, (255, 255, 255), -1)

    cv2.ellipse(
        frame,
        (int(settings.WIDTH * 0.5), int(settings.HEIGHT * 1.12)),
        (int(settings.WIDTH * 0.75), int(settings.HEIGHT * 0.4)),
        0,
        0,
        360,
        (115, 205, 115),
        -1,
    )


def _overlay_title_image(frame, image, position):
    x, y = position
    height, width = image.shape[:2]
    roi = frame[y:y + height, x:x + width]

    if image.shape[2] == 4:
        alpha = image[:, :, 3:4].astype(np.float32) / 255.0
        roi[:] = (image[:, :, :3] * alpha + roi * (1.0 - alpha)).astype(np.uint8)
    else:
        roi[:] = image


# タイトル画面を表示し、開始キーまたは終了キーが押されるまで待つ。
def show_title_screen():
    cv2.namedWindow(settings.WINDOW_NAME, cv2.WINDOW_NORMAL)
    title_fruits = _load_title_fruits()
    japanese_font = _load_japanese_font()

    if settings.FULLSCREEN:
        cv2.setWindowProperty(
            settings.WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN,
        )

    while True:
        frame = np.zeros((settings.HEIGHT, settings.WIDTH, 3), dtype=np.uint8)
        _draw_title_background(frame)

        cv2.rectangle(frame, (55, 150), (735, 565), (245, 250, 255), -1)
        cv2.rectangle(frame, (55, 150), (735, 565), (80, 170, 245), 5)

        cv2.putText(
            frame,
            "Kids Fruit",
            (100, 270),
            cv2.FONT_HERSHEY_DUPLEX,
            2.4,
            (80, 105, 225),
            6,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            "Catch!",
            (100, 365),
            cv2.FONT_HERSHEY_DUPLEX,
            3.0,
            (45, 135, 245),
            7,
            cv2.LINE_AA,
        )
        _draw_japanese_text(
            frame,
            "体を動かして落ちてくるフルーツをキャッチしてね！",
            (100, 405),
            japanese_font,
        )
        cv2.putText(
            frame,
            "Press SPACE to Start",
            (100, 495),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (55, 135, 60),
            3,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            "Press ESC to Exit",
            (100, 535),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (70, 85, 95),
            2,
            cv2.LINE_AA,
        )

        for image, position in title_fruits:
            _overlay_title_image(frame, image, position)

        cv2.imshow(settings.WINDOW_NAME, frame)
        key = cv2.waitKey(30) & 0xFF

        if key == 27:
            return False
        if key == 32:
            return True


# ゲームのメインループ。タイトルを表示し、開始後にプレイを実行する。
def main():
    while True:
        start = show_title_screen()
        if not start:
            break

        game = FruitGame()
        game.run()

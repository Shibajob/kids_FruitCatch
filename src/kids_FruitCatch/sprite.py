import os

import cv2

from kids_FruitCatch import settings


# フルーツ画像を読み込み、ゲーム中に描画するための管理クラス。
class SpriteManager:
    def __init__(self):
        self.images = {}
        self.load_fruits()

    # PNG 画像を読み込み、ゲーム用のサイズにリサイズする。
    def load_fruits(self):
        if not os.path.exists(settings.FRUIT_DIR):
            raise FileNotFoundError(f"{settings.FRUIT_DIR} がありません。")

        for file in os.listdir(settings.FRUIT_DIR):
            if not file.lower().endswith(".png"):
                continue

            name = os.path.splitext(file)[0]
            path = os.path.join(settings.FRUIT_DIR, file)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            if img is None:
                continue

            img = cv2.resize(img, (settings.FRUIT_SIZE, settings.FRUIT_SIZE))
            self.images[name] = img

    def get_names(self):
        return list(self.images.keys())

    # 指定したフルーツの画像を、中心座標に合わせて描画する。
    def draw(self, frame, name, center_x, center_y):
        if name not in self.images:
            return

        png = self.images[name]
        h, w = png.shape[:2]

        x = int(center_x - w / 2)
        y = int(center_y - h / 2)

        self.overlay_png(frame, png, x, y)

    # PNG の透明部分を考慮して背景へ合成する。
    def overlay_png(self, frame, png, x, y):
        h, w = png.shape[:2]

        if x < 0 or y < 0:
            return
        if x + w > frame.shape[1] or y + h > frame.shape[0]:
            return

        if png.shape[2] == 3:
            frame[y:y + h, x:x + w] = png
            return

        roi = frame[y:y + h, x:x + w]
        alpha = png[:, :, 3] / 255.0

        for c in range(3):
            roi[:, :, c] = alpha * png[:, :, c] + (1 - alpha) * roi[:, :, c]

        frame[y:y + h, x:x + w] = roi

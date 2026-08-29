import cv2
import random
import math
import time
import os
from datetime import datetime

from kids_FruitCatch import settings
from kids_FruitCatch.sprite import SpriteManager
from kids_FruitCatch.pose_detector import PoseDetector


# ゲーム全体の状態管理とフレーム更新を担当するクラス。
class FruitGame:

    def __init__(self):
        # カメラを起動し、画面サイズに合わせて設定を適用する。
        self.cap = cv2.VideoCapture(0)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            settings.WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            settings.HEIGHT
        )

        cv2.namedWindow(
            settings.WINDOW_NAME,
            cv2.WINDOW_NORMAL
        )

        if settings.FULLSCREEN:
            cv2.setWindowProperty(
                settings.WINDOW_NAME,
                cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN
            )

        # ゲーム要素の初期化。
        self.sprite = SpriteManager()
        self.detector = PoseDetector()

        self.recording = False
        self.writer = None
        self.records_folder = os.path.join(os.getcwd(), "records")

        os.makedirs(self.records_folder, exist_ok=True)

        self.score = 0
        self.fruits = []
        self.last_spawn = time.time()
        self.effect_until = 0
        self.effect_position = (0, 0)
        self.effect_text = ""

    # フルーツの初期位置と速度をランダムに設定する。
    def create_fruit(self):
        return {
            "x": random.randint(
                settings.FRUIT_RADIUS,
                settings.WIDTH - settings.FRUIT_RADIUS
            ),
            "y": -settings.FRUIT_SIZE,
            "speed": random.randint(
                settings.FRUIT_SPEED_MIN,
                settings.FRUIT_SPEED_MAX
            ),
            "type": random.choice(self.sprite.get_names())
        }

    # 一定時間ごとに新しいフルーツを生成する。
    def spawn(self):
        if time.time() - self.last_spawn > settings.SPAWN_INTERVAL:
            self.fruits.append(self.create_fruit())
            self.last_spawn = time.time()

    # 画面外に出たフルーツを削除する。
    def update_fruits(self):
        remove = []

        for fruit in self.fruits:
            fruit["y"] += fruit["speed"]

            if fruit["y"] > settings.HEIGHT + settings.FRUIT_SIZE:
                remove.append(fruit)

        for fruit in remove:
            self.fruits.remove(fruit)

    # 体の座標とフルーツの距離を計り、当たり判定を行う。
    def check_collision(self, body_points):
        remove = []

        for fruit in self.fruits:
            hit = False

            for bx, by in body_points:
                distance = math.hypot(bx - fruit["x"], by - fruit["y"])

                if distance < settings.BODY_HIT_RADIUS:
                    self.score += settings.SCORE_PER_FRUIT
                    self.effect_text = "GOOD!"
                    self.effect_until = time.time() + max(settings.GOOD_EFFECT_TIME, 1.5)
                    self.effect_position = (fruit["x"], fruit["y"])
                    hit = True
                    break

            if hit:
                remove.append(fruit)

        for fruit in remove:
            self.fruits.remove(fruit)

    # 現在のフルーツを画面に描画する。
    def draw_fruits(self, frame):
        for fruit in self.fruits:
            self.sprite.draw(frame, fruit["type"], fruit["x"], fruit["y"])

    # 捕まえたときの演出として「GOOD!」を表示する。
    def draw_effect(self, frame):
        if time.time() > self.effect_until:
            return

        x, y = self.effect_position

        cv2.putText(
            frame,
            self.effect_text,
            (int(x - 70), int(y - 80)),
            cv2.FONT_HERSHEY_DUPLEX,
            1.4,
            settings.YELLOW,
            4
        )

        cv2.circle(
            frame,
            (int(x), int(y)),
            60,
            settings.YELLOW,
            3
        )

    # スコアと録画状態を画面に表示する。
    def draw_score(self, frame):
        cv2.rectangle(
            frame,
            (0, 0),
            (320, 90),
            settings.BLACK,
            -1
        )

        cv2.putText(
            frame,
            f"Score : {self.score}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            settings.WHITE,
            3
        )
        self.draw_recording_indicator(frame)

    # 1 フレームごとのゲーム更新処理。
    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (settings.WIDTH, settings.HEIGHT))

                body_points = self.detector.detect(frame)
                self.detector.draw(frame, body_points)

                self.spawn()
                self.update_fruits()
                self.check_collision(body_points)

                self.draw_fruits(frame)
                self.draw_effect(frame)
                self.draw_score(frame)

                cv2.putText(
                    frame,
                    "ESC : EXIT",
                    (settings.WIDTH - 260, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    settings.WHITE,
                    2
                )

                if self.recording and self.writer is not None:
                    try:
                        self.writer.write(frame)
                    except Exception:
                        pass

                cv2.imshow(settings.WINDOW_NAME, frame)
                key = cv2.waitKey(1) & 0xFF

                if key == 27:
                    break

                if key == ord("r"):
                    if not self.recording:
                        self.start_recording()
                    else:
                        self.stop_recording()
        finally:
            self.close()

    # カメラや MediaPipe を安全に終了処理する。
    def close(self):
        self.detector.release()
        self.cap.release()

        if self.writer is not None:
            try:
                self.writer.release()
            except Exception:
                pass

        cv2.destroyAllWindows()

    # 録画開始時に VideoWriter を準備する。
    def start_recording(self):
        if self.recording:
            return

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.records_folder, f"record_{ts}.mp4")

        try:
            self.writer = cv2.VideoWriter(
                filename,
                fourcc,
                20.0,
                (settings.WIDTH, settings.HEIGHT)
            )

            if not self.writer.isOpened():
                self.writer = None
                return

            self.recording = True
        except Exception:
            self.writer = None
            self.recording = False

    # 録画中の保存を停止し、ファイルを閉じる。
    def stop_recording(self):
        if not self.recording:
            return

        try:
            if self.writer is not None:
                self.writer.release()
        except Exception:
            pass

        self.writer = None
        self.recording = False

    # 録画中であることを画面右上に視覚的に表示する。
    def draw_recording_indicator(self, frame):
        if not self.recording:
            return

        cv2.circle(
            frame,
            (settings.WIDTH - 60, 40),
            12,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            "REC",
            (settings.WIDTH - 110, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )



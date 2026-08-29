import math
import os
import time
import warnings

import cv2

# MediaPipe の古い protobuf 互換性により、既知の非推奨警告を抑制する。
warnings.filterwarnings(
    "ignore",
    message=r"SymbolDatabase\.GetPrototype\(\) is deprecated",
    category=UserWarning,
    module=r"google\.protobuf\.symbol_database",
)

import mediapipe as mp

from kids_FruitCatch import settings


# MediaPipe を用いて人体のランドマークを検出し、ゲーム判定に使うクラス。
class PoseDetector:
    def __init__(self):
        # MediaPipe の初期化時に出るネイティブログを抑えて、ゲーム画面を汚さない。
        stderr_fd = os.dup(2)

        try:
            with open(os.devnull, "w") as devnull:
                os.dup2(devnull.fileno(), 2)
                self.pose = mp.solutions.pose.Pose(
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                time.sleep(1.0)
        finally:
            os.dup2(stderr_fd, 2)
            os.close(stderr_fd)

        # MediaPipe のランドマーク番号を、ゲーム内で使う部位名に対応付ける。
        self.ids = {
            "nose": 0,
            "l_shoulder": 11,
            "r_shoulder": 12,
            "l_elbow": 13,
            "r_elbow": 14,
            "l_wrist": 15,
            "r_wrist": 16,
            "l_hip": 23,
            "r_hip": 24,
            "l_knee": 25,
            "r_knee": 26,
            "l_ankle": 27,
            "r_ankle": 28,
        }

    # 2 点の間を補間して、体の中心線上にも判定点を増やす。
    def _interpolate(self, p1, p2, step=30):
        x1, y1 = p1
        x2, y2 = p2

        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return [p1]

        count = max(1, int(dist / step))
        pts = []

        for i in range(count + 1):
            t = i / count
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            pts.append((x, y))

        return pts

    # 1 フレーム分の姿勢を検出し、当たり判定用の座標群を返す。
    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)

        if not result.pose_landmarks:
            return []

        h, w = frame.shape[:2]
        points = {}

        for name, idx in self.ids.items():
            lm = result.pose_landmarks.landmark[idx]
            if lm.visibility < settings.POSE_VISIBILITY:
                continue
            points[name] = (int(lm.x * w), int(lm.y * h))

        body = []
        body.extend(points.values())

        # 肩・腕・脚の間に補間点を追加して、判定の精度を上げる。
        bones = [
            ("nose", "l_shoulder"),
            ("nose", "r_shoulder"),
            ("l_shoulder", "r_shoulder"),
            ("l_shoulder", "l_elbow"),
            ("l_elbow", "l_wrist"),
            ("r_shoulder", "r_elbow"),
            ("r_elbow", "r_wrist"),
            ("l_shoulder", "l_hip"),
            ("r_shoulder", "r_hip"),
            ("l_hip", "r_hip"),
            ("l_hip", "l_knee"),
            ("l_knee", "l_ankle"),
            ("r_hip", "r_knee"),
            ("r_knee", "r_ankle"),
        ]

        for a, b in bones:
            if a not in points or b not in points:
                continue
            body.extend(self._interpolate(points[a], points[b]))

        return body

    # デバッグ用に骨格ポイントを描画する。設定で表示を切り替え可能。
    def draw(self, frame, body_points):
        if not settings.SHOW_BODY_POINTS:
            return

        for x, y in body_points:
            cv2.circle(frame, (x, y), 5, settings.BLUE, -1)

    def release(self):
        self.pose.close()


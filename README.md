# Kids Fruit Catch

子ども向けの体を動かすゲーム「Kids Fruit Catch」。
カメラでプレイヤーの動きを検出し、手や体で落ちてくるフルーツをキャッチします。

## 概要
- カメラ入力を使ったリアルタイムゲーム
- 録画機能（`r`キーで開始/停止）を搭載
- タイトル画面（`SPACE`でゲーム開始、`ESC`で終了）

## 現在のプロジェクト構成
- ソースコード: `src/kids_FruitCatch/`（パッケージ名: `kids_FruitCatch`）
- 実行用ラッパー: `main.py`（プロジェクトルート）
- 画像: `images/fruits/`（PNG画像を追加するとゲーム内に読み込まれます）
- 録画出力: `records/`（自動作成、`.gitignore` に追加済み）

主なファイル:
- `src/kids_FruitCatch/top.py` - タイトル画面とゲーム起動処理
- `src/kids_FruitCatch/game.py` - ゲーム本体（描画、ゲームループ、録画制御）
- `src/kids_FruitCatch/pose_detector.py` - 姿勢検出（MediaPipe 依存）
- `src/kids_FruitCatch/sprite.py` - 画像・スプライト管理
- `src/kids_FruitCatch/settings.py` - 画面や挙動の設定

## 必要な環境
- Python 3.11 以上（3.11 で動作確認済み）
- カメラ（Webカメラ等）

## 依存パッケージ
依存は `requirements.txt` にまとめてあります。Python 3.11の仮想環境を作成して以下を実行してください:

```powershell
pip install -r requirements.txt
```

## 実行方法
プロジェクトルートで次のいずれかを実行してください:

- 簡単実行（推奨）:

```powershell
python main.py
```

- もしくはパッケージとして直接起動（`src` を PYTHONPATH に追加する必要あり）:

```powershell
$env:PYTHONPATH='src'; python -m kids_FruitCatch.top
```

パッケージを開発モードでインストールすると、`kids-FruitCatch` コマンドが使えます:

```powershell
pip install -e .
kids-FruitCatch
```

操作:
- タイトル画面: `SPACE` を押してゲーム開始、`ESC` で終了
- ゲーム中: `r` で録画の開始/停止（録画は `records/` に mp4 で保存）
- ゲーム終了: `ESC`

## exeの作成
仮想環境を有効にした後、プロジェクトルートでPyInstallerをインストールします:

```powershell
.\venv\Scripts\Activate.ps1
pip install -e ".[build]"
```

続けて、次のコマンドでexeを作成してください。`--collect-data mediapipe` は姿勢検出に必要なMediaPipeのモデルファイルを同梱するために必要です。

```powershell
$imagePath = (Resolve-Path .\images).Path
pyinstaller --noconfirm --clean --onefile --windowed `
  --name kids_FruitCatch --distpath exe --workpath build\pyinstaller --specpath build `
  --paths src `
  --collect-submodules kids_FruitCatch `
  --add-data "$imagePath;images" `
  --collect-data mediapipe `
  main.py
```

生成された `exe/kids_FruitCatch.exe` を実行してください。`exe/` はGit管理対象外です。

## 録画について
- 録画ファイルはワークスペース内の `records` フォルダに
  `record_YYYYMMDD_HHMMSS.mp4` の形式で保存されます。
- 録画中は画面右上に赤い `REC` インジケータが表示されます。

## 設定の変更
- 画面解像度やフルスクリーン設定、当たり判定などは `src/kids_FruitCatch/settings.py` を編集してください。

## 開発・デバッグ
- カメラが認識されない場合はカメラデバイスが他プロセスで使用中でないか確認してください。
- MediaPipe起動時の既知のログは、姿勢検出器の初期化処理で抑制されます。

## 追加実装案
- マイク音声を同時に録音して動画と結合する（要 ffmpeg 等）
- 録画設定（FPS、コーデック）を `settings.py` から制御可能にする
- スコアやリプレイ機能の保存

## ライセンス
MIT ライセンス（LICENSE ファイルを参照）


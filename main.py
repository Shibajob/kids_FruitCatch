import sys
from pathlib import Path

# 開発実行時だけ src 配下を Python の検索パスへ追加する。
# これで `python main.py` のような実行でもパッケージを import できる。
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from kids_FruitCatch.top import main


if __name__ == "__main__":
    main()

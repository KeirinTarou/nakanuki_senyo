## メモ
- Python3.12を使用
    - pillowとの相性の問題？
```bash
py --3.12 -m venv .venv
```

- コマンドラインで実行
    - `nakanuki_senyo`ディレクトリをカレントディレクトリにして実行
```bash
python run.py
```

- pyinstallerコマンド
    - `nakanuki_senyo`ディレクトリをカレントディレクトリにして実行
```bash
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name nakanuki ^
    --add-data "src/resources/nakanuki.ico;." ^
    --add-data "src/resources/breakline.png;." ^
    --icon src/resources/nakanuki.ico ^
    run.py
```
- 各オプション
    - --onefile: 
        - 1つのEXEに固める
    - --noconsole
        - コンソールなしで起動
    - --name <base_name>
        - EXEファイルのベースネーム
    - --add-data <src;dest>
        - 外部ファイルのバインド
    - --icon
        - 実行ファイルのアイコンのパス



## プロジェクトのディレクトリ構成
```bash
nakanuki_senyo/
├── .venv/
│
├── src/
│   ├── nakanuki_core/ 
│   │   ├── __init__.py 
│   │   └── nakanuki.py     # 中抜き処理ロジック
│   ├── nakanuki_gui/ 
│   │   ├── __init__.py 
│   │   └── main.py         # GUIエントリポイント
│   └── resources/ 
│       ├── nakanuki.ico 
│       └── breakline.png 
│
├── test_assets/            # テストで使用する素材画像
│   ├── BA-90.png
│   └── ...
│
├── tests/
│   ├── __init__.py 
│   ├── test_basic.py       # pytest 
│   └── test_....py
│
├── config.py
├── run.py                  # python run.py で GUI 起動補助
├── pytest.ini
├── requirements.txt
├── memo.md
└── .gitignore

```

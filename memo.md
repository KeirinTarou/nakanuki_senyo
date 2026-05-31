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

## fixtureについて
- `tests`ディレクトリ直下の`conftest.py`に書いたフィクスチャは、テストファイルでインポートしなくても呼び出すことができる
- `@pytest.fixture`デコレータを付けた関数を定義し、テストファイル側から呼び出して利用する
    - テスト関数の引数リストに追加するだけでOK
    - 例: `test_some_test_function(some_fixture):`
        - これだけで、関数ブロック内で`fixture`がフィクスチャで定義した機能を持ってふるまう

### 事例集
#### tkinter.Tkインスタンスを代用する
```py
@pytest.fixture
def tk_root(monkeypatch):
    # iconbitmap無効化
    monkeypatch.setattr(
        tk.Tk, "iconbitmap", lambda self, *a, **k: None)
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
```
- テスト用に細工をした`tkinter.Tk`インスタンスを返すフィクスチャ
- 細工の内容
    - `monkeypatch.setattr(tk.Tk, "iconbitmap", lambda self, *a, **k: None)`: 
        - `Tk`クラスの`iconbitmap()`メソッドを、〝引数で何を渡しても`None`を返すメソッド〟に差し替え
    - `root.withdraw()`: 
        - ウィンドウを非表示にする
        - 「withdraw」は「引っ込める」という意味の英単語
- `return`ではなく`yield`で返しているので、テストが終わった時点で次の`root.destroy()`に制御が移る
    - teardownができる

#### カスタムImageProcessorインスタンスを代用する
```py
class DummyImage:
    size = (100, 200)

class DummyProc:
    def __init__(self, path):
        self.image = DummyImage()
    def calc_display_size(self, img, max_w, max_h):
        return 50, 100, 0.5
    def resize_for_display(self, img, w, h):
        return img
    
@pytest.fixture
def dummy_proc():
    return DummyProc
```
- テスト用に`ImageProcessor`クラスを偽装した`DummyProc`クラスのインスタンスを返すフィクスチャ
- `ImageProcessor`が内包しておくべき`PIL.Image`オブジェクトも`DummyImage`クラスに差し替え
    - 画像サイズだけを偽装すれば良い
    - -> 固定で`(100, 200)`にしておく
- `DummyProc`には、`ImageProcessor`クラスが持つメソッドを最低限の実装で再現
    - `image`属性
        - `PIL.Image`オブジェクトを偽装した`DummyImage`オブジェクトをセット
    - `display_size()`メソッド
        - 固定で`(50, 100, 0.5)`を返す
    - `resize_for_display()`メソッド
        - 固定で`DummyImage`オブジェクトを返す

#### 画像処理（含画像オブジェクトへの依存）を代用する
```py
@pytest.fixture
def patch_image_dependencies(monkeypatch, dummy_proc):
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageProcessor", dummy_proc)
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageTk.PhotoImage", 
        lambda * _: object())
```
- `main`モジュールにインポートされる次のクラスを差し替えるフィクスチャ
    - カスタム`ImageProcessor`クラス
        - -> `dummy_proc`フィクスチャに差し替え
    - 画像をTkinterで表示するための`ImageTk.PhotoImage`クラス
        - -> 何もしない空のオブジェクトに差し替え
        - `lambda * _: object()`: 
            - 引数に何が渡されても`object()`を返す
            - `_`は引数を受け取るための変数
            - `* _`なので、〝可変長引数〟、つまり複数の引数を受け取った場合はタプルとして`_`で受け取ることになる
            - 利用しない変数であることを明示するため慣例に従い`_`を用いる
- `main`モジュールで定義されている`NakanukiApp.load_image()`メソッド実行時の画像読み込み処理を偽装する

#### ファイルダイアログを代用する
```py
@pytest.fixture
def mock_file_dialog(tmp_path):
    test_img = tmp_path / "sample.png"
    test_img.touch()

    with patch(
        "src.nakanuki_gui.main.filedialog.askopenfilename", 
        return_value=str(test_img)):
        yield test_img
```
- ファイルダイアログによるファイルパス受け取りを差し替えるフィクスチャ
- `main`モジュールにインポートされる`filedialog`クラスの`askopenfilename()`メソッドを偽装する
- フィクスチャ内で、一時フォルダ（`tmp_path`）に`sample.png`という偽の画像ファイルを作成
- `askopenfilename()`メソッドの返り値を`sample.png`のパス（文字列）に差し替え
- `test_img`（`Path`オブジェクト）を返す
    - この例の場合は、後処理がないので`return`でも動く
    - ただ、フィクスチャの場合は〝後処理がある〟前提なので、`yield`を用いる

## `main.py`
```py
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from pathlib import Path
from datetime import datetime
from typing import Tuple

from config import (resource_path, RESOURCES_DIR, IMG_DISPLAY_SIZE)
from src.nakanuki_core.nakanuki import nakanuki_image
from src.nakanuki_core.image_processor import ImageProcessor

ICON_PATH = RESOURCES_DIR / "nakanuki.ico"

class NakanukiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("中抜専用")
        self.root.geometry("640x480")
        self.root.resizable(False, False)
        root.iconbitmap(ICON_PATH)

        # プレビュー領域
        self.canvas = tk.Canvas(
            root, bg="gray", width=600, height=400)
        self.canvas.pack(pady=10)

        # 画像データ
        self.original_image = None
        self.display_image = None
        self.display_scale = 1.0
        self.canvas_image_id = None

        # スピンボックス
        spin_frame = tk.Frame(root)
        spin_frame.pack()

        self.var_height = tk.StringVar(value="Height: - px")
        self.var_from = tk.StringVar()
        self.var_to = tk.StringVar()
        self.var_add_break_line = tk.BooleanVar(value=False)

        self.lbl_height = tk.Label(
            spin_frame, 
            textvariable=self.var_height
        )
        self.lbl_height.pack(side=tk.LEFT, padx=10)

        tk.Label(spin_frame, text="From").pack(side=tk.LEFT, padx=5)
        self.spin_from = tk.Spinbox(
            spin_frame, from_=0, to=9999, width=6, 
            textvariable=self.var_from, command=self.update_lines)
        self.spin_from.pack(side=tk.LEFT)

        tk.Label(spin_frame, text="To").pack(side=tk.LEFT, padx=5)
        self.spin_to = tk.Spinbox(
            spin_frame, from_=0, to=9999, width=6, 
            textvariable=self.var_to, command=self.update_lines)
        self.spin_to.pack(side=tk.LEFT)

        tk.Checkbutton(
            spin_frame, text="省略線追加", 
            variable=self.var_add_break_line
        ).pack(side=tk.LEFT, padx=10)

        # trace 追加
        self.var_from.trace_add("write", lambda *args: self.update_lines())
        self.var_to.trace_add("write", lambda *args: self.update_lines())

        # ボタン群
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(
            btn_frame, 
            text="画像を開く", 
            command=self.load_image
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame, 
            text="中抜き！", 
            command=self.nakanuki_and_save
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame, 
            text="終了", 
            command=root.quit
        ).pack(side=tk.LEFT, padx=5)

        # ラインID保持
        self.line_ids = []

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("画像ファイル", "*.png;*.jpg;*.jpeg")]
        )
        if not path:
            return
        
        self.src_path = Path(path)

        # 元画像のImageオブジェクト取得 -> original_imageにセット
        # 画像の取得・加工はImageProcessorに委譲
        proc = ImageProcessor(path)
        self.original_image = proc.image
        img = self.original_image
        w, h = img.size
        # 画像高さ表示ラベルを更新
        self.var_height.set(f"Height: {h} px")

        # 表示用に縮小
        # リサイズ用のサイズを取得
        max_w, max_h = IMG_DISPLAY_SIZE[0], IMG_DISPLAY_SIZE[1]
        display_w, display_h, scale = proc.calc_display_size(img, max_w, max_h)
        # display_scale属性にセット
        self.display_scale = scale
        # リサイズ後画像を取得
        resized = proc.resize_for_display(img, display_w, display_h)
        self.display_image = ImageTk.PhotoImage(resized)

        # キャンバス中央に画像を表示
        self.canvas.delete("all")
        center_x, center_y = max_w / 2, max_h / 2
        self.canvas.create_image(center_x, center_y, image=self.display_image)

        # Spinboxの最大値調整
        self.spin_from.config(to=h)
        self.spin_to.config(to=h)

    def update_lines(self):
        """ 水平線の更新"""
        if not self.original_image:
            return
        
        # 既存のラインをポア
        for lid in self.line_ids:
            self.canvas.delete(lid)
        self.line_ids.clear()
        # スピンボタンから値を取得
        try:
            y_from = int(self.spin_from.get())
            y_to = int(self.spin_to.get())
        except ValueError:
            return
        
        # From、Toの始点・終点の座標のタプルを取得
        # 表示領域の大きさ
        disp_w, disp_h = IMG_DISPLAY_SIZE[0], IMG_DISPLAY_SIZE[1]
        # 元画像の大きさ
        img = self.display_image
        img_w, img_h = img.width(), img.height()
        (xf0, yf0, xf1, yf1), (xt0, yt0, xt1, yt1) = \
            self._calc_horizontal_line_coords(
                (disp_w, disp_h), (img_w, img_h) , 
                self.display_scale, y_from, y_to)
        # ライン描画
        line1 = \
            self.canvas.create_line(xf0, yf0, xf1, yf1, fill="red", width=2)
        line2 = \
            self.canvas.create_line(xt0, yt0, xt1, yt1, fill="red", width=2)
        self.line_ids = [line1, line2]

    def nakanuki_and_save(self):
        """ 画像を中抜きしてエクスポート"""
        if not self.original_image:
            return
        
        try:
            y_from = int(self.spin_from.get())
            y_to = int(self.spin_to.get())
        except ValueError:
            return
        
        if y_from >= y_to:
            # 不正範囲は黙って無視
            return
        
        img = self.original_image
        rgbed = img.convert("RGB")
        add_break_line = self.var_add_break_line.get()
        out = nakanuki_image(rgbed, y_from, y_to, add_break_line)

        # ファイル名生成
        src = self.src_path
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"{src.stem}_{ts}{src.suffix}"

        save_dir = src.parent
        out.save(save_dir / out_name)
    
    # Internal methods
    @staticmethod
    def _calc_horizontal_line_coords( 
            img_display_size: Tuple[int, int], 
            img_pixel_size: Tuple[int, int], 
            display_scale: float, 
            y_from: int, 
            y_to: int
    ) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
        """ キャンバスに表示する中抜き範囲の水平線の座標を求める
        :param img_display_size: 表示領域のサイズ
        :type img_display_size: Tuple[int, int]
        :param img_pixle_size: 元画像のサイズ
        :type img_pixel_size: Tuple[int, int]
        :param display_scale: 表示倍率
        :type display_scale: float
        :param y_from: 中抜きの開始座標
        :type y_from: int
        :param y_to: 中抜きの終了座標
        :type y_to: int
        :return: 2本の水平線の始点・終点座標を詰め込んだタプル
        :rtype: Tuple[Tuple[int, int], Tuple[int, int]]
        """
        # 水平線のx座標は、From、To2本とも 0 ～ キャンバス右端
        x0 = 0
        x1 = img_display_size[0]
        # 表示領域の高さ
        h_disp = img_display_size[1]
        # 画像の高さ
        h_img = img_pixel_size[1]
        
        # Fromの水平線: 
        #   y座標: 
        # キャンバス中心のy座標から画像サイズの半分を引く
        # ただしマイナスにはならない
        y_disp_center = int(h_disp / 2)
        # 画像高さの半分
        h_img_half = int(h_img / 2)
        # キャンバス配置後の画像の上端のy座標
        # 画像がキャンバスよりも小さい場合は正の数になる
        # 画像がキャンバスよりも大きい場合は縮小されるので0未満にはならない
        h_img_top = max(y_disp_center - h_img_half, 0)
        y_from_disp = int(h_img_top + (y_from * display_scale))

        # Toの水平線
        # キャンバス配置後の画像の下端のy座標
        # 画像の下端よりも大きくはならない
        h_img_bottom = min(y_disp_center + h_img_half, h_disp)
        y_to_disp = int(min(h_img_top + (y_to * display_scale), h_img_bottom))

        line1 = (x0, y_from_disp, x1, y_from_disp)
        line2 = (x0, y_to_disp, x1, y_to_disp)

        return line1, line2

def main():
    root = tk.Tk()
    app = NakanukiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

## nakanuki.py
```py
from PIL import Image

from config import resource_path

def nakanuki_image(
        img: Image.Image, 
        y_from: int, 
        y_to: int, 
        add_break_line: bool=False) -> Image.Image:
    """ 中抜き後のImage.Imageオブジェクトを返す
    
    :param img: 中抜き前のImage.Imageオブジェクト
    :type img: Image.Image
    :param y_from: 中抜き開始座標
    :type y_from: int
    :param y_to: 中抜き終了座標
    :type y_to: int
    :param add_break_line: 省略線を入れるかどうか
    :type add_break_line: bool
    :return: 中抜き後のImage.Imageオブジェクト
    :rtype: Image.Image
    ..note::
        - src/nakanuki_core/nakanuki.py
    """
    if y_from >= y_to:
        raise ValueError("y_from must be less than y_to.")
    
    w, h = img.size

    y_from = max(0, min(y_from, h))
    y_to = max(0, min(y_to, h))

    top = img.crop((0, 0, w, y_from))
    bottom = img.crop((0, y_to, w, h))

    new_h = top.height + bottom.height
    out = Image.new(img.mode, (w, new_h))

    out.paste(top, (0, 0))
    out.paste(bottom, (0, top.height))

    if add_break_line:
        break_img = Image.open(resource_path("breakline.png"))
        # break_img = Image.open(RESOURCES_DIR / "breakline.png")
        if break_img.mode != "RGBA":
            break_img = break_img.convert("RGBA")
        break_img = break_img.resize((w, 40), Image.LANCZOS)
        y = top.height - break_img.height // 2
        out.paste(break_img, (0, y), mask=break_img)

    return out

```

## conftest.py
```py
import tkinter as tk
import pytest
from unittest.mock import patch

@pytest.fixture
def tk_root(monkeypatch):
    # iconbitmap無効化
    monkeypatch.setattr(
        tk.Tk, "iconbitmap", lambda self, *a, **k: None)
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

# ImageProcessorを偽装
class DummyImage:
    size = (100, 200)

class DummyProc:
    def __init__(self, path):
        self.image = DummyImage()
    def calc_display_size(self, img, max_w, max_h):
        return 50, 100, 0.5
    def resize_for_display(self, img, w, h):
        return img
    
@pytest.fixture
def dummy_proc():
    return DummyProc

@pytest.fixture
def mock_file_dialog(tmp_path):
    test_img = tmp_path / "sample.png"
    test_img.touch()

    with patch(
        "src.nakanuki_gui.main.filedialog.askopenfilename", 
        return_value=str(test_img)):
        yield test_img

@pytest.fixture
def patch_image_dependencies(monkeypatch, dummy_proc):
    monkeypatch.setattr("src.nakanuki_gui.main.ImageProcessor", dummy_proc)
    monkeypatch.setattr("src.nakanuki_gui.main.ImageTk.PhotoImage", lambda * _: object())

```

## test_save_path.py
```py
from pathlib import Path

def test_save_path_load_image_sets_src_path(
        tk_root, monkeypatch, patch_image_dependencies, mock_file_dialog):
    """ ファイルダイアログからファイルパスを受け取ることができる"""
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)

    app.load_image()
    # NakanukiAppのsrc_pathとテスト用ファイルのパスが一致するはず
    assert app.src_path == mock_file_dialog

def test_save_path_save_uses_src_directory(
        tk_root, monkeypatch, patch_image_dependencies, mock_file_dialog):
    from src.nakanuki_gui.main import NakanukiApp
    app = NakanukiApp(tk_root)

    monkeypatch.setattr(app.canvas, "delete", lambda *a, **k: None)
    monkeypatch.setattr(app.canvas, "create_image", lambda *a, **k: None)

    app.src_path = mock_file_dialog

    class DummyImage:
        def convert(self, mode):
            return self
        filename = str(mock_file_dialog)

    app.original_image = DummyImage()

    # 必要なUIパーツ群
    app.spin_from = type("", (), {"get": lambda self: "10"})()
    app.spin_to = type("", (), {"get": lambda self: "20"})()
    app.var_add_break_line = type("", (), {"get": lambda self: False})()

    # 保存パス取得
    saved_path = {}

    def fake_save(path):
        saved_path["path"] = path

    class DummyOut:
        def save(self, path):
            fake_save(path)

    monkeypatch.setattr(
        "src.nakanuki_gui.main.nakanuki_image", 
        lambda *a, **k: DummyOut())
    
    # 実行
    app.nakanuki_and_save()

    # 保存ファイルの親フォルダが元ファイルの親フォルダと一致するはず
    assert saved_path["path"].parent == mock_file_dialog.parent

```

## テストに関するメモ
### ✅ conftest.py に引き上げるべき項目
```py
# ダミーオブジェクトクラスを集約
class DummyImage:
class DummyOutImage:
class DummySpinbox:
class DummyPhotoImage:
class DummyProc:

# 頻出するモック化フィクスチャ
@pytest.fixture
def image_fixture():
    """複数サイズの test_image をパラメータ化"""

@pytest.fixture
def test_image_path():
    """test_assets の画像を使用"""
```

### 🎯 追加すべきテストケース
1. ImageProcessor クラス
- ❌ 存在しないファイルパスを渡した場合
- ❌ 無効な画像形式を渡した場合
- ❌ None 状態の画像に resize_for_display() を呼ぶ
- ✅ RGBA など異なる画像モードへの対応
2. nakanuki_image() 関数
- ✅ 基本的な中抜きはカバー済み
- ❌ add_break_line=True の詳細検証
- ❌ 異なる画像フォーマット（RGBA、グレースケール）での動作
3. GUI 統合テスト
- ❌ 画像ロード→中抜き→保存 の一連フロー
- ❌ エラーハンドリング（不正ファイル選択時）
- ❌ ウィジェット状態の同期性
4. エッジケース
- ❌ 0px 以下の画像に対する処理
- ❌ y_from = y_to のケース（現在の仕様では？）
- ❌ 1x1 ピクセルの極小画像

### 📝 推奨される再構成案
```bash
tests/
├── conftest.py                  # すべてのダミーオブジェクト、共通フィクスチャ
├── unit/
│   ├── test_nakanuki_image.py          # 中抜きロジック
│   ├── test_image_processor.py         # 画像処理クラス
│   └── test_edge_cases.py              # 新規：エッジケース
├── integration/
│   └── test_app_workflow.py            # 新規：GUI全体フロー
└── fixtures/
    └── test_assets.py                  # 新規：画像パスのヘルパー
```

```py
# `conftest.py`の変更案
import pytest
from PIL import Image

class DummyImage:
    def __init__(self, size=(100, 200), mode="RGB"):
        self.size = size
        self.mode = mode

    def convert(self, mode):
        return self


class DummyOutImage:
    def __init__(self, size=(100, 70)):
        self.size = size

    def save(self, path):
        path.write_text("dummy")


class DummySpinbox:
    def __init__(self, value):
        self.value = value
        self.max_value = None

    def get(self):
        return self.value

    def config(self, **kwargs):
        if "to" in kwargs:
            self.max_value = kwargs["to"]


class DummyBooleanVar:
    def __init__(self, value=False):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

class DummyProc:
    def __init__(self, path):
        self.image = DummyImage()

    def calc_display_size(self, img, max_w, max_h):
        return 50, 100, 0.5

    def resize_for_display(self, img, w, h):
        return img

class DummyPhotoImage:
    def width(self):
        return 50

    def height(self):
        return 100

@pytest.fixture
def tk_root(monkeypatch):
    # iconbitmap無効化
    monkeypatch.setattr(
        tk.Tk, "iconbitmap", lambda self, *a, **k: None)
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def dummy_proc():
    return DummyProc

@pytest.fixture
def dummy_image():
    return DummyImage()

@pytest.fixture
def dummy_out_image():
    return DummyOutImage()

@pytest.fixture
def dummy_spinbox():
    return DummySpinbox

@pytest.fixture
def dummy_boolean_var():
    return DummyBooleanVar(False)

@pytest.fixture
def sample_image_path(tmp_path):
    test_img = tmp_path / "sample.png"
    Image.new("RGB", (100, 100)).save(test_img)
    return test_img

@pytest.fixture
def patch_image_dependencies(monkeypatch, dummy_proc):
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageProcessor", dummy_proc)
    monkeypatch.setattr(
        "src.nakanuki_gui.main.ImageTk.PhotoImage",
        lambda *_, **__: DummyPhotoImage())

@pytest.fixture
def mock_file_dialog(tmp_path):
    test_img = tmp_path / "sample.png"
    Image.new("RGB", (100, 100)).save(test_img)

    with patch(
        "src.nakanuki_gui.main.filedialog.askopenfilename",
        return_value=str(test_img),
    ):
        yield test_img
```

```py
# `test_apply_nakanuki.py`

from src.nakanuki_gui.main import NakanukiApp

def test_apply_nakanuki_updates_spinbox_max(
        tk_root, monkeypatch, dummy_spinbox, dummy_boolean_var,
        dummy_image, dummy_out_image):
    """ 「中抜き適用」ボタンクリック -> スピンボックスの最大値更新"""
    app = NakanukiApp(tk_root)

    app.original_image = dummy_image
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("20")
    app.var_add_break_line = dummy_boolean_var
    
    monkeypatch.setattr(
        app,
        "_show_image_on_canvas",
        lambda img: None
    )
    
    monkeypatch.setattr(
        app,
        "_nakanuki_exec",
        lambda: dummy_out_image
    )

    monkeypatch.setattr(
        app,
        "update_lines",
        lambda: None
    )

    app.apply_nakanuki()

    assert app.spin_from.max_value == 70
    assert app.spin_to.max_value == 70

def test_apply_nakanuki_updates_current_height(
        tk_root, monkeypatch, dummy_spinbox, dummy_boolean_var,
        dummy_image, dummy_out_image):
    """ ｢中抜適用｣ボタンクリック -> 画像の高さ更新"""
    app = NakanukiApp(tk_root)

    app.original_image = dummy_image
    app.spin_from = dummy_spinbox("10")
    app.spin_to = dummy_spinbox("20")
    app.var_add_break_line = dummy_boolean_var
    
    # _show_image_on_canvas()乗っ取り
    monkeypatch.setattr(
        app, 
        "_show_image_on_canvas", 
        lambda img: None
    )
    # _nakanuki_exec()乗っ取り
    monkeypatch.setattr(
        app, 
        "_nakanuki_exec", 
        lambda: dummy_out_image
    )
    # update_lines()乗っ取り
    monkeypatch.setattr(
        app, 
        "update_lines", 
        lambda: None
    )
    # apply_nakanuki()実行
    app.apply_nakanuki()

    # ラベルに表示される画像高さは中抜き後の70のはず
    assert app.var_height.get() == "Height: 70 px"

```
## メモ
- コマンドラインで実行
    - `nakanuki_senyo`ディレクトリをカレントディレクトリにして実行
```bash
python run.py
```

- pyinstallerコマンド
    - `nakanuki_senyo`ディレクトリをカレントディレクトリにして実行
```bash
pyinstaller --onefile --noconsole --name nakanuki --add-data "src/resources/nakanuki.ico;." --icon src/resources/nakanuki.ico run.py
```

## プロジェクトのディレクトリ構成
```bash
nakanuki_senyo/
├── src/
│   ├── nakanuki_core/ 
│   │   ├── __init__.py 
│   │   └── nakanuki.py     # 中抜き処理ロジック
│   ├── nakanuki_gui/ 
│   │   ├── __init__.py 
│   │   └── main.py         # GUIエントリポイント
│   └── resources/ 
│       └── nakanuki.ico 
│
├── tests/
│   ├── __init__.py 
│   └── test_basic.py       # pytest
│
├── run.py                  # python run.py で GUI 起動補助
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore

```

## `main.py`
```py
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path
import sys
from datetime import datetime

from app.nakanuki import nakanuki_image

if hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = BASE_DIR / "img" / "nakanuki.ico"

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

        self.var_from = tk.StringVar()
        self.var_to = tk.StringVar()
        self.var_height = tk.StringVar(value="Height: - px")

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
        
        self.original_image = Image.open(path)
        w, h = self.original_image.size
        # 画像高さ表示ラベルを更新
        self.var_height.set(f"Height: {h} px")

        # 表示用に縮小
        scale = min(600 / w, 400 / h, 1)
        self.display_scale = scale

        display_w = int(w * scale)
        display_h = int(h * scale)

        resized = self.original_image.resize(
            (display_w, display_h), Image.LANCZOS)
        self.display_image = ImageTk.PhotoImage(resized)

        # キャンバス中央に画像を表示
        self.canvas.delete("all")
        # 300, 200はキャンバスの中心座標
        self.canvas.create_image(300, 200, image=self.display_image)

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

        try:
            y_from = int(self.spin_from.get())
            y_to = int(self.spin_to.get())
        except ValueError:
            return
        
        # 画像縮小を考慮したキャンバス上座標に変換
        y_from_disp = int(y_from * self.display_scale)
        y_to_disp = int(y_to * self.display_scale)

        # プレビュー画像の表示位置（中央固定）
        # 画像のTopLeft座標を取得
        x0 = 300 - self.display_image.width() // 2
        y0 = 200 - self.display_image.height() // 2

        # ライン描画
        line1 = self.canvas.create_line(
            x0, y0 + y_from_disp, x0 + self.display_image.width(), 
            y0 + y_from_disp, fill="red", width=2)
        line2 = self.canvas.create_line(
            x0, y0 + y_to_disp, x0 + self.display_image.width(), 
            y0 + y_to_disp, fill="red", width=2)
        
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
        out = nakanuki_image(img, y_from, y_to)

        # ファイル名生成
        src = Path(img.filename)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"{src.stem}_{ts}{src.suffix}"

        save_dir = Path.home() / "Downloads"
        out.save(save_dir / out_name)

def main():
    root = tk.Tk()
    app = NakanukiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

## `run.py`
```py
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).parent

sys.path.insert(0, str(base_dir))

from app.main import main

if __name__ == "__main__":
    main()
```

## nakanuki.py
```py
from PIL import Image

def nakanuki_image(
        img: Image.Image, 
        y_from: int, 
        y_to: int) -> Image.Image:
    """ 中抜き後のImage.Imageオブジェクトを返す
    
    :param img: 中抜き前のImage.Imageオブジェクト
    :type img: Image.Image
    :param y_from: 中抜き開始座標
    :type y_from: int
    :param y_to: 中抜き終了座標
    :type y_to: int
    :return: 中抜き後のImage.Imageオブジェクト
    :rtype: Image.Image
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

    return out

```
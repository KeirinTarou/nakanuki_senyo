import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from pathlib import Path
from datetime import datetime
from typing import Tuple
import traceback
from PIL import Image

from config import (resource_path, CANVAS_SIZE)
from src.nakanuki_core.nakanuki import nakanuki_image
from src.nakanuki_core.image_processor import ImageProcessor

ICON_PATH = resource_path("nakanuki.ico")

class NakanukiApp:
    def __init__(self, root):
        # tkinter.Tkインスタンス
        self.root = root
        self.root.title("中抜専用")
        self.root.geometry("640x480")
        self.root.resizable(False, False)
        root.iconbitmap(ICON_PATH)

        # プレビュー領域
        canv_w, canv_h = CANVAS_SIZE
        self.canvas = tk.Canvas(
            root, bg="gray", width=canv_w, height=canv_h)
        self.canvas.pack(pady=10)

        # 画像データ
        self.original_image = None
        self.display_image = None
        self.display_scale = 1.0
        self.canvas_image_id = None

        # GUIから取得した値を格納する属性群
        self.var_height = tk.StringVar(value="Height: - px")
        self.var_from = tk.StringVar()
        self.var_to = tk.StringVar()
        self.var_add_break_line = tk.BooleanVar(value=False)

        # ラインID保持用属性
        self.line_ids = []

        # UIパーツ群（1段目）
        # スピンボックス用（画像サイズ用ラベル・チェックボックス含む）用フレーム
        spin_frame = tk.Frame(root)
        spin_frame.pack()
        # 画像の高さを表示するラベル
        self.lbl_height = tk.Label(
            spin_frame, 
            textvariable=self.var_height
        )
        self.lbl_height.pack(side=tk.LEFT, padx=10)
        # 「From」スピンボックス
        tk.Label(spin_frame, text="From").pack(side=tk.LEFT, padx=5)
        self.spin_from = tk.Spinbox(
            spin_frame, from_=0, to=9999, width=6, 
            textvariable=self.var_from, command=self.update_lines)
        self.spin_from.pack(side=tk.LEFT)
        # 「To」スピンボックス
        tk.Label(spin_frame, text="To").pack(side=tk.LEFT, padx=5)
        self.spin_to = tk.Spinbox(
            spin_frame, from_=0, to=9999, width=6, 
            textvariable=self.var_to, command=self.update_lines)
        self.spin_to.pack(side=tk.LEFT)
        # 「省略線追加」チェックボックス
        tk.Checkbutton(
            spin_frame, text="省略線追加", 
            variable=self.var_add_break_line
        ).pack(side=tk.LEFT, padx=10)

        # trace 追加
        self.var_from.trace_add("write", lambda *args: self.update_lines())
        self.var_to.trace_add("write", lambda *args: self.update_lines())

        # UIパーツ群（2段目）
        # ボタンを収めるフレーム
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        # 「画像を開く」ボタン
        tk.Button(
            btn_frame, 
            text="画像を開く", 
            command=self.load_image
        ).pack(side=tk.LEFT, padx=5)
        # 「中抜き！」ボタン
        tk.Button(
            btn_frame, 
            text="中抜き！", 
            command=self.nakanuki_and_save
        ).pack(side=tk.LEFT, padx=5)
        # 「終了」ボタン
        tk.Button(
            btn_frame, 
            text="終了", 
            command=root.quit
        ).pack(side=tk.LEFT, padx=5)

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
        max_w, max_h = CANVAS_SIZE[0], CANVAS_SIZE[1]
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
        disp_w, disp_h = CANVAS_SIZE[0], CANVAS_SIZE[1]
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
        out = self._nakanuki_exec()
        if out is None:
            return

        # ファイル名生成
        src = Path(self.original_image.filename)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"{src.stem}_{ts}{src.suffix}"

        try:
            save_dir = self.src_path.parent
            save_path = save_dir / out_name
            out.save(save_path)
            log(f"Saved: {save_path}")
        except Exception:
            log("ERROR saving:")
            log(traceback.format_exc())
    
    def _nakanuki_exec(self) -> Image.Image | None:
        """ 画像の中抜き処理を行う"""
        if not self.original_image:
            return None
        
        try:
            y_from = int(self.spin_from.get())
            y_to = int(self.spin_to.get())
        except ValueError:
            return None
        
        # # 不正範囲 -> None
        if y_from >= y_to:
            return None
        
        # オリジナル画像
        img = self.original_image
        # RGBに変換
        rgbed = img.convert("RGB")
        # 省略線フラグ
        add_break_line = self.var_add_break_line.get()

        try:
            out = nakanuki_image(rgbed, y_from, y_to, add_break_line)
        except Exception:
            log("ERROR in nakanuki: ")
            log(traceback.format_exc())
            return None
        
        return out

    # Internal methods
    @staticmethod
    def _calc_horizontal_line_coords( 
            canvas_size: Tuple[int, int], 
            img_pixel_size: Tuple[int, int], 
            display_scale: float, 
            y_from: int, 
            y_to: int
    ) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
        """ キャンバスに表示する中抜き範囲の水平線の座標を求める
        :param canvas_size: 表示領域のサイズ
        :type canvas_size: Tuple[int, int]
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
        x1 = canvas_size[0]
        # 表示領域の高さ
        h_canv = canvas_size[1]
        # 画像の高さ
        h_img = img_pixel_size[1]
        
        # Fromの水平線: 
        #   y座標: 
        # キャンバス中心のy座標から画像サイズの半分を引く
        # ただしマイナスにはならない
        y_canv_center = int(h_canv / 2)
        # 画像高さの半分
        h_img_half = int(h_img / 2)
        # キャンバス配置後の画像の上端のy座標
        # 画像がキャンバスよりも小さい場合は正の数になる
        # 画像がキャンバスよりも大きい場合は縮小されるので0未満にはならない
        h_img_top = max(y_canv_center - h_img_half, 0)
        y_from_canv = int(h_img_top + (y_from * display_scale))

        # Toの水平線
        # キャンバス配置後の画像の下端のy座標
        # 画像の下端よりも大きくはならない
        h_img_bottom = min(y_canv_center + h_img_half, h_canv)
        y_to_canv = int(min(h_img_top + (y_to * display_scale), h_img_bottom))

        line1 = (x0, y_from_canv, x1, y_from_canv)
        line2 = (x0, y_to_canv, x1, y_to_canv)

        return line1, line2

LOG = Path.home() / "Downloads"

def log(s):
    with open(LOG / "nakanuki.log", "a", encoding="utf-8") as f:
        f.write(str(s) + "\n")

def main():
    root = tk.Tk()
    app = NakanukiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
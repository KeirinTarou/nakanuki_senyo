from PIL import Image
from typing import Tuple

class ImageProcessor:
    """ 画像加工を受け持つクラス

    ..note::
        - /src/nakanuki_core/image_processor.py 
    """
    def __init__(self, filepath:str=None):
        self.image = None
        if filepath is not None:
            self.load(filepath)

    def load(self, filepath: str) -> Image.Image:
        """ 画像をロードしてImageオブジェクトを返す

        :param filepath: 画像ファイルのパス
        :type filepath: str
        :return: Imageオブジェクト
        :rtype: Image
        .. note::
            - src/nakanuki_core/image_processor.py
        """
        try:
            img = Image.open(filepath)
        except (FileNotFoundError, OSError) as e:
            raise ValueError(f"Failed to load image: {filepath}") from e
        self.image = img
        return img
    
    def calc_display_size(
            self, img: Image.Image | None=None, 
            max_w: int=600, max_h: int=400) -> Tuple[int, int, float]:
        """ 表示用リサイズ後のサイズのタプルを返す
        
        :param img: Imageオブジェクト
        :type img: Image | None
        :param max_w: リサイズ後の画像の最大幅
        :type max_w: int
        :param max_h: リサイズ後の画像の最大高さ
        :type max_w: int
        :return: リサイズ後の幅、高さ、表示倍率のタプル
        :rtype: Tuple[int, int, float]
        .. note::
            - src/nakanuki_core/image_processor.py
        """
        if img is None:
            img = self.image
        # ガード
        if img is None:
            raise ValueError("calc_display_size: image is not loaded.")
        w, h = img.size
        scale = min(max_w / w, max_h / h, 1)
        return int(w * scale), int(h * scale), scale
    
    def resize_for_display(
            self, img: Image.Image | None, 
            display_w: int, display_h: int) -> Image.Image:
        """ Tkinter描画用の縮小画像を返す
        
        :param img: リサイズ後の画像
        :type img: Image.Image | None
        :param display_w: 表示サイズ（幅）
        :type display_w: int
        :param display_h: 表示サイズ（高さ）
        :type display_h: int
        :return: リサイズ後のImage.Imageオブジェクト
        :rtype: Image.Image
        """
        if img is None:
            img = self.image
        # ガード
        if img is None:
            raise ValueError("calc_display_size: image is not loaded.")
        return img.resize((display_w, display_h), Image.LANCZOS)
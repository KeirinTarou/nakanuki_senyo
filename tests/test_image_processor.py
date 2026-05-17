import pytest
from PIL import Image
from src.nakanuki_core.image_processor import ImageProcessor

def test_image_processor_load(tmp_path):
    """ 画像のファイルパスから画像をロードできる"""
    img_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100)).save(img_path)
    proc = ImageProcessor(img_path)
    img = proc.image
    assert isinstance(img, Image.Image)
    assert img.size == (100, 100)

def test_image_processor_calc_display_size():
    """ 表示画像サイズと倍率を計算することができる"""
    img = Image.new("RGB", (900, 600))
    proc = ImageProcessor()
    w, h, scale = proc.calc_display_size(img, 450, 200)
    # より倍率の低い方に合わせるはず
    assert scale == 1/ 3
    assert (w, h) == (300, 200)

def test_image_processor_resize_for_display():
    img = Image.new("RGB", (100, 100))
    proc = ImageProcessor()
    resized = proc.resize_for_display(img, 50, 50)
    assert isinstance(img, Image.Image)
    assert resized.size == (50, 50)

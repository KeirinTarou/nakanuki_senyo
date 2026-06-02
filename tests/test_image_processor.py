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
    w, h, scale = ImageProcessor.calc_display_size(900, 600, 450, 200)
    # より倍率の低い方に合わせるはず
    assert scale == 1/ 3
    assert (w, h) == (300, 200)

def test_image_processor_calc_display_size_width_provided_zero():
    """ widthに0が渡された -> 例外スロー"""
    with pytest.raises(ValueError):
        ImageProcessor.calc_display_size(0, 100)

def test_image_processor_calc_display_size_height_provided_zero():
    """ heightに0が渡された -> 例外スロー"""
    with pytest.raises(ValueError):
        ImageProcessor.calc_display_size(100, 0)

def test_image_processor_calc_display_size_max_w_provided_zero():
    """ max_wに0が渡された -> 例外スロー"""
    with pytest.raises(ValueError):
        ImageProcessor.calc_display_size(100, 100, 0, 400)

def test_image_processor_calc_display_size_max_h_provided_zero():
    """ max_hに0が渡された -> 例外スロー"""
    with pytest.raises(ValueError):
        ImageProcessor.calc_display_size(100, 100, 600, 0)

def test_image_processor_resize_for_display():
    img = Image.new("RGB", (100, 100))
    proc = ImageProcessor()
    resized = proc.resize_for_display(img, 50, 50)
    assert isinstance(img, Image.Image)
    assert resized.size == (50, 50)

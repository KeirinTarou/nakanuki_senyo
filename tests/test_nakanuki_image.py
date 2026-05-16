from PIL import Image
import pytest

from src.nakanuki_core.nakanuki import nakanuki_image

#  TODO:
#   ✅- 100 x 100の画像を30-70で中抜き -> 100 x 60の画像
#   ✅- FromよりToが小さい -> ValueError例外を吐く
#   ✅- y_fromが負の数のときは0に丸める
#   ✅- y_fromが画像高さを少しでも超えたら画像高さに丸める
#   ✅- y_fromが画像高さを超えるときは画像高さに丸める

def test_nakanuki_image_normal():
    """ 100 x 100の画像を30-70で中抜き -> 100 x 60の画像"""
    img = Image.new("RGB", (100, 100))
    result = nakanuki_image(img, 30, 70)
    assert result.width == 100
    assert result.height == 60

def test_nakanuki_image_invalid_range():
    """ FromよりToが小さい -> ValueError例外を吐く"""
    img = Image.new("RGB", (100, 100), "white")
    with pytest.raises(ValueError):
        nakanuki_image(img, 70, 30)

def test_nakanuki_image_clamp_behavior():
    """ y_from < 0 は0に補正"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, -10, 50)
    assert result.width == 100
    assert result.height == 50

def test_nakanuki_image_y_to_upper_bound_clamp():
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 30, 101)
    assert result.width == 100
    assert result.height == 30

def test_nakanuki_image_y_to_extreme_upper_value():
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 30, 999)
    assert result.width == 100
    assert result.height == 30

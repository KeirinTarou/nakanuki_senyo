from PIL import Image
import pytest

from src.nakanuki_core.nakanuki import nakanuki_image

# 中抜処理を行うnakanuki_image()関数の動作保証テスト

#  TODO:
#   ✅- 100 x 100の画像を30-70で中抜き -> 100 x 60の画像
#   ✅- FromよりToが小さい -> ValueError例外を吐く
#   ✅- 0以外でFromとToが同じ -> ValueError例外を吐く
#   ✅- 中抜き後のサイズが0 -> ValueError例外を吐く
#   ✅- y_fromが負の数のときは0に丸める
#   ✅- y_fromが画像高さを少しでも超えたら画像高さに丸める
#   ✅- y_fromが画像高さを超えるときは画像高さに丸める
#   ✅- FromとToがともに0 -> 元の画像を返す
#   ✅- 省略線オン/オフで結果が変わる
#   ✅- add_break_lineをTrueにすると省略線を追加する
#   ✅- 中抜き画像の外側にはみ出した省略線はカットされる
#   ✅- 中抜き後、画像モードが維持される

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

def test_nakanuki_image_no_range():
    """ 0以外でFromとToが同じ -> ValueError例外を吐く"""
    img = Image.new("RGB", (100, 100), "white")
    with pytest.raises(ValueError):
        nakanuki_image(img, 50, 50)

def test_nakanuki_image_cropped_height_must_be_positive():
    """ 中抜き後のサイズが0 -> ValueError例外を吐く"""
    img = Image.new("RGB", (100, 100), "white")
    with pytest.raises(ValueError):
        nakanuki_image(img, 0, 100)

def test_nakanuki_image_clamp_behavior():
    """ y_from < 0 は0に補正"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, -10, 50)
    assert result.width == 100
    assert result.height == 50

def test_nakanuki_image_y_to_upper_bound_clamp():
    """ y_fromが画像高さを少しでも超えたら画像高さに丸める"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 30, 101)
    assert result.width == 100
    assert result.height == 30

def test_nakanuki_image_y_to_extreme_upper_value():
    """ y_fromが画像高さを超えるときは画像高さに丸める"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 30, 999)
    assert result.width == 100
    assert result.height == 30

def test_nakanuki_image_same_values_provided():
    """ FromとToがともに0 -> 元の画像を返す"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 0, 0)
    assert result is img

def test_nakanuki_image_add_break_line_causes_difference():
    """ 省略線オン/オフで結果が変わる"""
    img = Image.new("RGB", (100, 100), "white")
    # 中抜きサイズは同じで省略線の有無のみ異なる
    result1 = nakanuki_image(img, 30, 70, True)
    result2 = nakanuki_image(img, 30, 70, False)
    # 省略線の有無で画像のサイズが変わる
    assert result1.tobytes() != result2.tobytes()

def test_nakanuki_image_add_break_line(monkeypatch):
    """ add_break_lineをTrueにすると省略線を追加する"""
    img = Image.new("RGB", (100, 100), "white")
    # 赤一色のダミー省略線を作る
    dummy_break_img = \
        Image.new("RGBA", (100, 40), (255, 0, 0, 255))
    
    # nakanukiモジュール内の`Image.open()`を差し替え
    # どんなpathが渡されても`dummy_break_img`を返す
    monkeypatch.setattr(
        "src.nakanuki_core.nakanuki.Image.open", 
        lambda path: dummy_break_img)
    
    # nakanuki_image()で中抜き & ダミー省略線貼り付け実行
    # 30 - 70の範囲を中抜きし、省略線を施す
    result = \
        nakanuki_image(img, 30, 70, add_break_line=True)
    
    # 省略線の範囲内のピクセルは赤のはず
    assert result.getpixel((50, 30)) == (255, 0, 0)
    # 省略線の範囲外のピクセルは白のはず
    assert result.getpixel((50, 5)) == (255, 255, 255)

def test_nakanuki_image_break_line_is_clipped_when_overflow(monkeypatch):
    """ 中抜き画像の外側にはみ出した省略線はカットされる"""
    img = Image.new("RGB", (100, 100), "white")
    # 赤一色のダミー省略線を作る
    dummy_break_img = \
        Image.new("RGBA", (100, 40), (255, 0, 0, 255))
    
    # nakanukiモジュール内の`Image.open()`を差し替え
    # どんなpathが渡されても`dummy_break_img`を返す
    monkeypatch.setattr(
        "src.nakanuki_core.nakanuki.Image.open", 
        lambda path: dummy_break_img)
    
    # nakanuki_image()で中抜き & ダミー省略線貼り付け実行
    # 10 - 50の範囲を中抜きし、省略線を施す
    result = \
        nakanuki_image(img, 10, 50, add_break_line=True)
    
    # 省略線の上10ピクセル分が中抜き後画像の外にはみ出してカットされるはず
    # 中抜き後画像の上端のピクセルは赤のはず
    assert result.getpixel((50, 0)) == (255, 0, 0)
    # 中抜き後画像の上から30ピクセル目のピクセルも赤のはず
    assert result.getpixel((50, 29)) == (255, 0, 0)
    # 中抜き後画像の上から31ピクセル目のピクセルが白のはず
    assert result.getpixel((50, 30)) == (255, 255, 255)

@pytest.mark.parametrize(
        "mode", ["RGB", "RGBA", "L"])
def test_nakanuki_image_preserve_image_mode(mode):
    """ 中抜き後、画像モードが維持される
    
    .. note::
    - @pytest.mark.parametrize()使用
        - `mode`にリスト内の3つのパラメータを順に割り当てる
        - パラメータの数だけテストを行う
    """
    img = Image.new(mode, (100, 100))
    result = nakanuki_image(img, 30, 70)
    assert result.mode == mode
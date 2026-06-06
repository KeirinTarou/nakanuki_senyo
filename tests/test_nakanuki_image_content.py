from PIL import Image

from src.nakanuki_core.nakanuki import nakanuki_image

# nakanuki_image()による処理後の画像が壊れていないことを保証するテスト

# TODO: -> ✅DONE
#   ✅- 中抜き処理で画像の幅は変わらない
#   ✅- 中抜き後の高さが正しく計算されている
#   ✅- 中抜き後、上部領域が完全に残る 
#   ✅- 中抜き後、下部領域が完全に残り、正しく上に詰められる
#   ✅- 省略線オン/オフで結果が変わる
#   ✅- add_break_lineをTrueにすると省略線を追加する
#   ✅- 中抜き画像の外側にはみ出した省略線はカットされる

def test_nakanuki_image_content_width_is_unchange():
    """ 中抜き処理で画像の幅は変わらない"""
    img = Image.new("RGB", (100, 100))
    result = nakanuki_image(img, 30, 70)
    assert result.width == img.width

def test_nakanuki_image_content_height_is_correct():
    """ 中抜き後の高さが正しく計算されている"""
    img = Image.new("RGB", (100, 100))
    y_from = 30
    y_to = 70
    result = nakanuki_image(img, y_from, y_to)
    expected_height = img.height - (y_to - y_from)
    assert result.height == expected_height

def test_nakanuki_image_content_top_region_is_preserved():
    """ 中抜き後、上部領域が完全に残る"""
    img = Image.new("RGB", (10, 10))
    # 上半分を赤、下半分を青にする
    for y in range(10):
        for x in range(10):
            if y < 5:
                img.putpixel((x, y), (255, 0, 0))
            else:
                img.putpixel((x, y), (0, 0, 255))
    y_from = 3
    y_to = 7
    result = nakanuki_image(img, y_from, y_to)
    # 上部（0 ～ 2行）は完全に残るはず
    for y in range(y_from):
        for x in range(10):
            assert result.getpixel((x, y)) == img.getpixel((x, y))

def test_nakanuki_image_content_bottom_region_is_preserved_and_shifted():
    """ 中抜き後、下部領域が完全に残り、正しく上に詰められる"""
    img = Image.new("RGB", (10, 10))
    # 上半分を赤、下半分を青にする
    for y in range(10):
        for x in range(10):
            if y < 5:
                img.putpixel((x, y), (255, 0, 0))
            else:
                img.putpixel((x, y), (0, 0, 255))
    y_from = 3
    y_to = 7
    result = nakanuki_image(img, y_from, y_to)
    # 下部（7 ～ 9行）はresultの3 ～ 5に詰められるはず
    offset = y_to - y_from
    for y in range(y_to, img.height):
        result_y = y - offset
        for x in range(img.width):
            assert result.getpixel((x, result_y)) == img.getpixel((x, y))

def test_nakanuki_image_content_add_break_line_causes_difference():
    """ 省略線オン/オフで結果が変わる"""
    img = Image.new("RGB", (100, 100), "white")
    # 中抜きサイズは同じで省略線の有無のみ異なる
    result1 = nakanuki_image(img, 30, 70, True)
    result2 = nakanuki_image(img, 30, 70, False)
    # 省略線の有無で画像のサイズが変わる
    assert result1.tobytes() != result2.tobytes()

def test_nakanuki_image_content_add_break_line(monkeypatch):
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

def test_nakanuki_image_content_break_line_is_clipped_when_overflow(monkeypatch):
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
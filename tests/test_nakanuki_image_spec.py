from PIL import Image

from src.nakanuki_core.nakanuki import nakanuki_image

# TODO: -> ✅DONE
#   ✅- 中抜き処理で画像の幅は変わらない
#   ✅- 中抜き後の高さが正しく計算されている
#   ✅- 中抜き後、上部領域が完全に残る 
#   ✅- 中抜き後、下部領域が完全に残り、正しく上に詰められる 


def test_nakanuki_image_spec_width_is_unchange():
    """ 中抜き処理で画像の幅は変わらない"""
    img = Image.new("RGB", (100, 100))
    result = nakanuki_image(img, 30, 70)
    assert result.width == img.width

def test_nakanuki_image_spec_height_is_correct():
    img = Image.new("RGB", (100, 100))
    y_from = 30
    y_to = 70
    result = nakanuki_image(img, y_from, y_to)
    expected_height = img.height - (y_to - y_from)
    assert result.height == expected_height

def test_nakanuki_image_spec_top_region_is_preserved():
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

def test_nakanuki_image_spec_bottom_region_is_preserved_and_shifted():
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

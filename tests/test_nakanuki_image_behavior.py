from PIL import Image

from src.nakanuki_core.nakanuki import nakanuki_image

# TODO:
#   ✅- 正しく中抜きされる
#   ✅- 画像モードが変わらない
#   ✅- 画像モードが変わらない
#   ✅- 保存後再読み込みしても壊れない
#   ✅- 中抜き後の画像が壊れていない
#   ✅- 中抜き後黒化していない
#   ✅- RGB変換して保存した画像をRGB形式で開くことができる
#   ✅- 中抜き後の画像をRGB変換しても壊れない 


def test_nakanuki_image_edge_pixels():
    """ 正しく中抜きされる"""
    img = Image.new("RGB", (100, 100))
    # 上半分を赤、下半分を青に塗る
    for y in range(100):
        for x in range(100):
            if y < 50:
                img.putpixel((x, y), (255, 0, 0))
            else:
                img.putpixel((x, y), (0, 0, 255))   
    result = nakanuki_image(img, 40, 60)
    # 上端のピクセルは残す上半分なので赤のはず
    assert result.getpixel((10, 0)) == (255, 0, 0)
    # 下端のピクセルは残す下半分なので青のはず
    assert result.getpixel((10, result.height - 1)) == (0, 0, 255)
    # 最終的な高さは中抜き後の高さのはず
    assert result.height == 80 # 100 - (60 - 40)

def test_nakanuki_image_rgba_basic():
    """ 中抜き後、画像モードが変わらない"""
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    result = nakanuki_image(img, 30, 70)

    # サイズは変わらないはず
    assert result.width == 100
    assert result.height == 60
    # modeが壊れていないはず
    assert result.mode == "RGBA"

def test_nakanuki_image_save_and_reload(tmp_path):
    """ 保存後再読み込みしても壊れていない"""
    img = Image.new("RGB", (100, 100), "white")
    result = nakanuki_image(img, 30, 70)
    file_path = tmp_path / "out.png"
    result.save(file_path)
    reloaded = Image.open(file_path)
    assert reloaded.size == result.size
    assert reloaded.mode == result.mode

def test_nakanuki_image_blacken_regression(tmp_path):
    """ 中抜き後の画像が壊れていない"""
    img = Image.open("test_assets/BA-90.png")
    result = nakanuki_image(img, 320, 520)
    out_path = tmp_path / "out.png"
    result.save(out_path)

    reloaded = Image.open(out_path)
    # 壊れていないことの検証
    assert reloaded.size == result.size

def test_nakanuki_image_pixel_integrity():
    """ 中抜き後黒化していない"""
    img = Image.open("test_assets/BA-90.png")
    result = nakanuki_image(img, 320, 520)
    # 黒化確認
    assert result.getpixel((10, 10)) != (0, 0, 0)

def test_nakanuki_image_rgb_conversion_save_roundtrip_(tmp_path):
    """ RGB変換して保存した画像をRGB形式で開くことができる"""
    img = Image.open("test_assets/BA-90.png")
    result = nakanuki_image(img, 320, 520)
    
    result = result.convert("RGB")
    out = tmp_path / "out.png"
    result.save(out)
    reloaded = Image.open(out)

    assert reloaded.mode == "RGB"

def test_nakanuki_image_metadata_agnostic_processing(tmp_path):
    """ 中抜き後の画像をRGB変換しても壊れない"""
    img = Image.open("test_assets/BA-90.png")
    result = nakanuki_image(img, 320, 520)
    # 強制RGB化
    result = result.convert("RGB")
    out = tmp_path / "out.png"
    result.save(out)

    reloaded = Image.open(out)
    assert reloaded.mode == "RGB"

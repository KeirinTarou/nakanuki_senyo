from PIL import Image

from config import resource_path

def nakanuki_image(
        img: Image.Image, 
        y_from: int, 
        y_to: int, 
        add_break_line: bool=False) -> Image.Image:
    """ 中抜き後のImage.Imageオブジェクトを返す
    
    :param img: 中抜き前のImage.Imageオブジェクト
    :type img: Image.Image
    :param y_from: 中抜き開始座標
    :type y_from: int
    :param y_to: 中抜き終了座標
    :type y_to: int
    :param add_break_line: 省略線を入れるかどうか
    :type add_break_line: bool
    :return: 中抜き後のImage.Imageオブジェクト
    :rtype: Image.Image
    ..note::
        - src/nakanuki_core/nakanuki.py
    """
    if y_from > y_to:
        raise ValueError("y_from must be less than y_to.")
    
    # y_from, y_toともに`0` -> そのまま元画像を返す
    if y_from == 0 and y_to == 0:
        return img
    
    w, h = img.size

    y_from = max(0, min(y_from, h))
    y_to = max(0, min(y_to, h))

    top = img.crop((0, 0, w, y_from))
    bottom = img.crop((0, y_to, w, h))

    new_h = top.height + bottom.height
    out = Image.new(img.mode, (w, new_h))

    out.paste(top, (0, 0))
    out.paste(bottom, (0, top.height))

    if add_break_line:
        break_img = Image.open(resource_path("breakline.png"))
        if break_img.mode != "RGBA":
            break_img = break_img.convert("RGBA")
        break_img = break_img.resize((w, 40), Image.LANCZOS)
        y = top.height - break_img.height // 2
        out.paste(break_img, (0, y), mask=break_img)

    return out